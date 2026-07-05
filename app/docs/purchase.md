# Purchase / Customer / Trip (đơn hàng, khách hàng, chuyến hàng)

Three modules implementing the **order lifecycle** of the hàng-xách-tay flow:
customer places an order → seller collects deposit → orders are consolidated
into a buying **trip** (gom đơn) or go solo (giao riêng) → purchases are
recorded with actual costs → goods arrive → delivery + final payment.

Module locations:
- `src/modules/customer/` — the shop's customer book
- `src/modules/purchase/` — Order aggregate (lines + payment receipts)
- `src/modules/trip/` — buying trips and consolidation

Follows the same DDD layout as [campaign](campaign.md):
`domain → application → infrastructure → presentation`, tenant isolation via
`organization_id` on every repository call, `DomainError → 400`,
NotFound → 404, conflicts → 409 (handlers in `src/app/application.py`).

`Money` now lives in `src/shared/domain/money.py` (moved from campaign, which
re-exports it for backward compatibility).

---

## 1. Concepts

| Concept | Meaning |
|---|---|
| **Customer** | Người mua của shop. Soft-delete (`active`); orders keep the reference forever. |
| **Order** | Đơn hàng của một khách — aggregate root chứa **OrderLine** và **PaymentReceipt**. |
| **OrderLine** | Một dòng hàng: product + snapshot tên/mã + số lượng + giá bán/cọc **nhập tự do** + tiến độ mua (`purchased_quantity`, `actual_unit_cost`). |
| **PaymentReceipt** | Phiếu thu — một lần nhận tiền (cọc, trả thêm, thu nốt). Totals are derived, never stored. |
| **TrackingCode** | Mã Code 8 ký tự cho khách tra cứu. **Globally unique** (public lookup page cần resolve không có org context). Alphabet bỏ ký tự dễ nhầm (0/O, 1/I/L). |
| **Trip** | Chuyến hàng gom nhiều đơn. Shopper (người xách tay) là **free text** — không phải user hệ thống; admin nhập mọi dữ liệu. |
| **is_separate** | "Giao riêng" — đơn đi lẻ, bị loại khỏi gom đơn. |

## 2. Architecture decisions

- **Order is the single aggregate root.** Lines and receipts are only reachable
  through it; money invariants (`total_amount`, `total_collected`, `remaining`)
  are computed on the aggregate, in one transaction. Repository loads the whole
  aggregate with `selectinload` and reconciles children diff-by-id on `save`.
- **Trip ↔ Order via nullable FK `orders.trip_id`** (no join table): one order
  belongs to at most one trip. Attach/detach are order-side mutations
  orchestrated by trip commands, allowed only while the trip is `planning`.
- **Status cascades run in the application layer** (same UoW/session → atomic):
  trip → `buying` moves attached orders to `purchasing`; trip → `arrived`
  moves them to `arrived`. Cross-aggregate rules stay out of the entities.
- **Product snapshot on lines** (`product_code`, `product_name`): an order must
  keep showing what was sold even if the catalog product is renamed later.
- **Free-form pricing**: `unit_price`/`unit_deposit` are typed by the seller;
  orders are *not* bound to a SaleRound/CampaignProduct.
- **Tracking-code generation**: `secrets.choice` over a 31-char alphabet,
  8 chars; pre-check `get_by_tracking_code` (up to 5 attempts) + DB unique
  constraint as the race backstop (`IntegrityError` → retryable 400).
- **`actual_unit_cost`** recorded per line during the trip is the seed data for
  the future P&L report (Giai đoạn 3).

## 3. Database model

```
organizations ─┬─< customers ──────< orders >────── trips >── (organizations)
               │                      │  │
               ├─< products ─────< order_lines      │
               │                      │             │
               └──────────────── order_receipts ────┘  (receipts belong to orders)
```

### customers
| column | type | notes |
|---|---|---|
| id | UUID PK | |
| organization_id | UUID FK → organizations | tenant |
| name | varchar(255) | |
| phone | varchar(32) NULL | not unique (Zalo/FB customers) |
| note | text | |
| active | bool | soft-delete |
| created_at / updated_at | timestamptz | `TimestampMixin` |

Index: `(organization_id, name)`.

### trips
| column | type | notes |
|---|---|---|
| id | UUID PK | |
| organization_id | UUID FK | tenant |
| code | varchar(64) | **unique per org** (`uq_trips_org_code`) |
| name | varchar(255) | |
| status | enum `trip_status` | planning \| buying \| shipping \| arrived \| completed \| cancelled |
| shopper_name | varchar(255) | free text — người xách tay |
| departure_date / arrival_date | date NULL | |
| note | text | |

Index: `(organization_id, status)`.

### orders
| column | type | notes |
|---|---|---|
| id | UUID PK | |
| organization_id | UUID FK | tenant |
| customer_id | UUID FK → customers | indexed |
| trip_id | UUID FK → trips, NULL | consolidation link, indexed |
| tracking_code | varchar(8) | **globally unique** (`uq_orders_tracking_code`) |
| status | enum `order_status` | pending \| confirmed \| purchasing \| purchased \| arrived \| delivered \| cancelled |
| is_separate | bool | giao riêng |
| note | text | |

Index: `(organization_id, status)`.

### order_lines
| column | type | notes |
|---|---|---|
| id | UUID PK | |
| order_id | UUID FK → orders ON DELETE CASCADE | indexed |
| product_id | UUID FK → products | |
| product_code / product_name | varchar | **snapshot** at order time |
| quantity | int ≥ 1 | |
| unit_price / unit_deposit | numeric(12,2) | free-form |
| purchased_quantity | int, default 0 | trip progress |
| actual_unit_cost | numeric(12,2) NULL | giá mua thực tế → P&L |
| purchased_at | timestamptz NULL | |

No denormalized org_id — lines are only reached through their order.

### order_receipts
| column | type | notes |
|---|---|---|
| id | UUID PK | |
| order_id | UUID FK → orders ON DELETE CASCADE | indexed |
| amount | numeric(12,2) | > 0 (enforced in `Order.add_receipt`) |
| method | enum `receipt_method` | cash \| bank_transfer \| other |
| received_at | timestamptz | |
| note | text | |

Derived (never stored): `total_amount = Σ qty×unit_price`,
`deposit_due = Σ qty×unit_deposit`, `total_collected = Σ receipts`,
`remaining = total_amount − total_collected`.

Migrations (in order): `a1c4e7b93f02` customers → `b7d2f5a81c43` trips →
`c9e6a3d47b18` orders + order_lines + order_receipts.

## 4. Status machines

**Order** (`ALLOWED_ORDER_TRANSITIONS` in `domain/value_objects/order.py`):
```
pending → confirmed → purchasing → purchased → arrived → delivered
   └──────────┴────────────┴─→ cancelled     (no cancel after purchased;
                                              no cancel while in a trip)
```
- `initial_receipt` on create ⇒ auto `pending → confirmed`.
- Recording purchases requires `purchasing`; when every line is fully bought
  the order auto-advances to `purchased`.

**Trip** (`ALLOWED_TRIP_TRANSITIONS` in `trip/domain/value_objects/trip.py`):
```
planning → buying → shipping → arrived → completed
    └─────────┴─→ cancelled
```
- Attach/detach orders: only while `planning`; order must be
  pending/confirmed, not giao riêng, not in another trip (violations → 409).
- `→ buying` cascades attached orders to `purchasing` (pending orders hop
  through `confirmed` so each step is a legal transition).
- `→ arrived` cascades `purchasing`/`purchased` orders to `arrived`.

## 5. API

All routes require `Authorization: Bearer <token>`; tenant comes from the user.

### /customers
| Method | Path | Notes |
|---|---|---|
| POST | `/customers` | 201 |
| GET | `/customers?search=&include_inactive=` | search matches name/phone (ILIKE) |
| GET | `/customers/{id}` | |
| PATCH | `/customers/{id}` | partial; `phone=""` clears |

### /orders
| Method | Path | Notes |
|---|---|---|
| POST | `/orders` | 201; `{customer_id, lines[], is_separate?, note?, initial_receipt?}` |
| GET | `/orders?status=&customer_id=&trip_id=&unassigned=` | `unassigned=true` = trip_id NULL + !is_separate (nguồn gom đơn) |
| GET | `/orders/{id}` | full read: lines, receipts, totals, customer_name |
| PATCH | `/orders/{id}` | note / is_separate / replace lines (PENDING only) |
| POST | `/orders/{id}/status` | validated transition |
| POST | `/orders/{id}/receipts` | 201; returns updated OrderRead |
| DELETE | `/orders/{id}/receipts/{receipt_id}` | 204 |
| POST | `/orders/{id}/lines/{line_id}/purchase` | `{purchased_quantity, actual_unit_cost?}`; works for trip and solo orders |

### /trips
| Method | Path | Notes |
|---|---|---|
| POST | `/trips` | 201; duplicate code → 409 |
| GET | `/trips?status=` | newest first |
| GET | `/trips/{id}` | |
| PATCH | `/trips/{id}` | name/shopper_name/dates/note |
| POST | `/trips/{id}/status` | validated + order cascade |
| GET | `/trips/{id}/orders` | orders in the trip (manifest gộp theo món tính ở client) |
| POST | `/trips/{id}/orders` | `{order_ids: []}` attach; violations → 409 |
| DELETE | `/trips/{id}/orders/{order_id}` | 204 detach (planning only) |

Money in/out: decimal numbers with 2 fraction digits (JSON numbers, e.g.
`550000.00`). Dates: ISO-8601.

## 6. Phase 3 additions (tra cứu, hoàn tiền, báo cáo)

- **Public tracking** — `GET /tracking/{code}` (router `presentation/public_routes.py`,
  **no auth**): safe view only (status, line names/quantities, totals) — no
  customer identity, no purchase costs, no tenant info. Malformed and unknown
  codes both return the same 404. Access control = the unguessable 31^8 code.
- **Refunds** — `order_receipts.kind` enum (`collection | refund`, migration
  `d5f8b2c61a94`). Amounts stay positive; `total_collected` = collections −
  refunds, `total_refunded` exposed on OrderRead. Rules in `Order.add_receipt`:
  collections are rejected on cancelled orders; refunds are allowed there
  (hoàn cọc khi hủy) but can never exceed the collected balance.
- **Reports** — module `src/modules/report/` (queries only, reuses purchase +
  customer repositories):
  - `GET /reports/profit?date_from=&date_to=&trip_id=` — per-order
    revenue / cost (Σ purchased_qty × actual_unit_cost) / profit / margin,
    `cost_complete` flag while some lines lack actuals, totals; cancelled
    orders excluded.
  - `GET /reports/receivables` — công nợ: every non-cancelled order with
    `remaining > 0`, sorted by amount owed, with `total_outstanding`.
- Push notifications (PRD Giai đoạn 3) deliberately deferred — needs Web Push
  infrastructure (VAPID keys, subscription storage, background sender).

## 7. Verified flow (smoke-tested end-to-end)

login → create product → create customer → create order + initial deposit
(tracking code 8 ký tự, totals đúng) → create trip → attach → trip `buying`
(order → `purchasing`) → record line purchase (order auto → `purchased`) →
trip `shipping` → `arrived` (order → `arrived`) → final receipt
(`remaining = 0`) → order `delivered`. Negatives: illegal transition 400,
duplicate trip code 409, attach giao-riêng 409, cross-org/random id 404,
no token 401.
