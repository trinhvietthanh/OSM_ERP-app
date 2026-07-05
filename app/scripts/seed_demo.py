"""Seed a realistic demo dataset (customers, products, orders, receipts, a
consolidated trip, purchases, a refund) by driving the running API.

Prereqs: migrations applied, admin seeded, API up on $API_BASE (default
http://localhost:8000).

    uv run uvicorn src.main:app --port 8000     # in another shell
    uv run python scripts/seed_demo.py

Idempotent guard: skips if the demo customer set already exists.
"""

import os
import sys

import httpx

API = os.environ.get("API_BASE", "http://localhost:8000")
EMAIL = os.environ.get("SEED_EMAIL", "admin@example.com")
PASSWORD = os.environ.get("SEED_PASSWORD", "admin12345")

PRODUCTS = [
    ("SRM-CELL", "Kem chống nắng Cell Fusion"),
    ("SERUM-VITC", "Serum Vitamin C Klairs"),
    ("TONER-ANUA", "Toner Anua Heartleaf 77%"),
    ("TPCN-DHC-B", "DHC Vitamin B Mix 60 ngày"),
    ("LIP-DIOR-999", "Son Dior 999 Velvet"),
    ("MASK-MEDIH", "Mặt nạ Mediheal N.M.F 10 miếng"),
]

CUSTOMERS = [
    ("Nguyễn Thị Mai", "0901111222", "khách quen, hay mua mỹ phẩm"),
    ("Trần Văn Hùng", "0902333444", ""),
    ("Lê Thị Hoa", "0903555666", "ưu tiên hàng Nhật"),
    ("Phạm Minh Tuấn", "0904777888", ""),
    ("Đỗ Thu Trang", "0905999000", "khách mới từ Facebook"),
    ("Vũ Thị Lan", "0906123456", "hay đặt son"),
]


def money(v: int) -> str:
    return str(v)


def main() -> None:
    with httpx.Client(base_url=API, timeout=30) as c:
        token = c.post(
            "/auth/login", json={"email": EMAIL, "password": PASSWORD}
        ).json()["access_token"]
        c.headers["Authorization"] = f"Bearer {token}"

        # Idempotency guard.
        existing = c.get("/customers", params={"search": "Nguyễn Thị Mai"}).json()
        if existing:
            print("[seed-demo] demo data already present — skipping.")
            return

        # --- products (skip if code already exists) ---
        have = {p["code"]: p["id"] for p in c.get("/catalog/products").json()}
        product_ids: dict[str, str] = {}
        for code, name in PRODUCTS:
            if code in have:
                product_ids[code] = have[code]
                continue
            r = c.post("/catalog/products", json={"code": code, "name": name})
            product_ids[code] = r.json()["id"]
        print(f"[seed-demo] products: {len(product_ids)}")

        # --- customers ---
        customer_ids = []
        for name, phone, note in CUSTOMERS:
            r = c.post("/customers", json={"name": name, "phone": phone, "note": note})
            customer_ids.append(r.json()["id"])
        print(f"[seed-demo] customers: {len(customer_ids)}")

        pid = list(product_ids.values())

        def create_order(cust, lines, note="", is_separate=False, deposit=None):
            body = {
                "customer_id": cust,
                "lines": lines,
                "note": note,
                "is_separate": is_separate,
            }
            if deposit is not None:
                body["initial_receipt"] = {
                    "amount": money(deposit),
                    "method": "bank_transfer",
                    "note": "Cọc khi tạo đơn",
                }
            return c.post("/orders", json=body).json()

        def status(order_id, st):
            c.post(f"/orders/{order_id}/status", json={"status": st})

        orders = []

        # 1) Pending order, no deposit yet (chờ xử lý).
        orders.append(
            create_order(
                customer_ids[0],
                [
                    {"product_id": pid[0], "quantity": 1, "unit_price": money(650000), "unit_deposit": money(200000)},
                    {"product_id": pid[1], "quantity": 2, "unit_price": money(320000), "unit_deposit": money(100000)},
                ],
                note="khách hỏi thêm màu",
            )
        )

        # 2) Confirmed with deposit (đã chốt) — will go into the trip.
        o2 = create_order(
            customer_ids[1],
            [{"product_id": pid[2], "quantity": 3, "unit_price": money(280000), "unit_deposit": money(100000)}],
            deposit=300000,
        )
        orders.append(o2)

        # 3) Confirmed with deposit (đã chốt) — will go into the trip.
        o3 = create_order(
            customer_ids[2],
            [
                {"product_id": pid[3], "quantity": 1, "unit_price": money(890000), "unit_deposit": money(400000)},
                {"product_id": pid[5], "quantity": 2, "unit_price": money(210000), "unit_deposit": money(80000)},
            ],
            deposit=560000,
        )
        orders.append(o3)

        # 4) Separate delivery (giao riêng) — never consolidated.
        orders.append(
            create_order(
                customer_ids[3],
                [{"product_id": pid[4], "quantity": 1, "unit_price": money(920000), "unit_deposit": money(500000)}],
                note="khách cần gấp, đi lẻ",
                is_separate=True,
                deposit=500000,
            )
        )

        # 5) A fully delivered order (paid in full) — for profit report.
        o5 = create_order(
            customer_ids[4],
            [{"product_id": pid[0], "quantity": 2, "unit_price": money(650000), "unit_deposit": money(200000)}],
            deposit=400000,
        )
        # advance to delivered, recording actual cost + final payment
        status(o5["id"], "purchasing")
        line = o5["lines"][0]
        c.post(
            f"/orders/{o5['id']}/lines/{line['id']}/purchase",
            json={"purchased_quantity": 2, "actual_unit_cost": money(430000)},
        )  # auto -> purchased
        status(o5["id"], "arrived")
        c.post(
            f"/orders/{o5['id']}/receipts",
            json={"amount": money(900000), "method": "cash", "note": "thu nốt khi giao"},
        )
        status(o5["id"], "delivered")
        orders.append(o5)

        # 6) A cancelled order with a refunded deposit.
        o6 = create_order(
            customer_ids[5],
            [{"product_id": pid[4], "quantity": 1, "unit_price": money(920000), "unit_deposit": money(300000)}],
            deposit=300000,
        )
        status(o6["id"], "cancelled")
        c.post(
            f"/orders/{o6['id']}/receipts",
            json={"amount": money(300000), "kind": "refund", "method": "bank_transfer", "note": "hoàn cọc do hủy"},
        )
        orders.append(o6)

        print(f"[seed-demo] orders: {len(orders)}")

        # --- consolidate orders 2 & 3 into a trip, run it to arrived ---
        trip = c.post(
            "/trips",
            json={
                "code": "JP-2026-07",
                "name": "Chuyến Nhật tháng 7",
                "shopper_name": "Anh Tuấn (người nhà)",
            },
        ).json()
        c.post("/trips/" + trip["id"] + "/orders", json={"order_ids": [o2["id"], o3["id"]]})
        c.post(f"/trips/{trip['id']}/status", json={"status": "buying"})  # orders -> purchasing

        # shopper (admin) records purchases for the trip's orders
        for od_id in (o2["id"], o3["id"]):
            od = c.get(f"/orders/{od_id}").json()
            for ln in od["lines"]:
                c.post(
                    f"/orders/{od_id}/lines/{ln['id']}/purchase",
                    json={
                        "purchased_quantity": ln["quantity"],
                        "actual_unit_cost": money(int(float(ln["unit_price"]) * 0.72)),
                    },
                )
        c.post(f"/trips/{trip['id']}/status", json={"status": "shipping"})
        c.post(f"/trips/{trip['id']}/status", json={"status": "arrived"})  # orders -> arrived
        print(f"[seed-demo] trip {trip['code']} → arrived, 2 orders purchased")

        # --- summary ---
        all_orders = c.get("/orders").json()
        by_status: dict[str, int] = {}
        for o in all_orders:
            by_status[o["status"]] = by_status.get(o["status"], 0) + 1
        print(f"[seed-demo] order status breakdown: {by_status}")
        recv = c.get("/reports/receivables").json()
        profit = c.get("/reports/profit").json()
        print(f"[seed-demo] receivables: {recv['orders_count']} orders, "
              f"{recv['total_outstanding']} outstanding")
        print(f"[seed-demo] profit: revenue {profit['total_revenue']}, "
              f"cost {profit['total_cost']}, profit {profit['total_profit']}")


if __name__ == "__main__":
    try:
        main()
    except httpx.HTTPError as exc:
        print(f"[seed-demo] HTTP error: {exc}", file=sys.stderr)
        sys.exit(1)
