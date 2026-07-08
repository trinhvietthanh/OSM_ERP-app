from datetime import UTC, datetime
from decimal import Decimal

from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderStatus
from src.modules.report.application.dto.report import (
    AgingBucketRead,
    ReceivableRead,
    ReceivablesReportRead,
    q2,
)

#: Aging buckets by order age in days: (key, inclusive upper bound).
_AGING_BUCKETS = (
    ("d0_7", 7),
    ("d8_30", 30),
    ("d31_60", 60),
    ("d61_plus", None),
)


def _aging_bucket(age_days: int) -> str:
    for key, upper in _AGING_BUCKETS:
        if upper is None or age_days <= upper:
            return key
    raise AssertionError("unreachable")


class ReceivablesReport:
    """Outstanding customer balances (công nợ): every non-cancelled order
    with remaining > 0, including delivered ones the customer still owes.

    Each debt is aged from the order's creation date into fixed buckets, and
    flagged when collections don't yet cover the agreed deposit (thiếu cọc).
    """

    def __init__(
        self,
        orders: AbstractOrderRepository,
        customers: AbstractCustomerRepository,
    ) -> None:
        self._orders = orders
        self._customers = customers

    async def execute(self, organization_id: OrganizationId) -> ReceivablesReportRead:
        orders = await self._orders.list(organization_id)
        names = {
            c.id_: c.name.value
            for c in await self._customers.list(organization_id, active_only=False)
        }
        now = datetime.now(UTC)

        rows: list[ReceivableRead] = []
        total = Decimal("0")
        total_billed = Decimal("0")
        total_collected = Decimal("0")
        total_deposit_due = Decimal("0")
        deposit_shortfall = Decimal("0")
        buckets = {key: [0, Decimal("0")] for key, _ in _AGING_BUCKETS}

        for order in orders:
            if order.status is OrderStatus.CANCELLED:
                continue
            remaining = order.remaining
            if remaining <= 0:
                continue
            age_days = max((now - order.created_at).days, 0)
            bucket = _aging_bucket(age_days)
            deposit_due = order.deposit_due
            collected = order.total_collected

            total += remaining
            total_billed += order.total_amount
            total_collected += collected
            total_deposit_due += deposit_due
            if collected < deposit_due:
                deposit_shortfall += deposit_due - collected
            buckets[bucket][0] += 1
            buckets[bucket][1] += remaining

            rows.append(
                ReceivableRead(
                    order_id=order.id_.value,
                    tracking_code=order.tracking_code.value,
                    customer_id=order.customer_id.value,
                    customer_name=names.get(order.customer_id, ""),
                    status=order.status.value,
                    total_amount=q2(order.total_amount),
                    total_collected=q2(collected),
                    remaining=q2(remaining),
                    created_at=order.created_at,
                    age_days=age_days,
                    aging_bucket=bucket,
                    deposit_due=q2(deposit_due),
                    deposit_covered=collected >= deposit_due,
                )
            )

        rows.sort(key=lambda r: r.remaining, reverse=True)
        return ReceivablesReportRead(
            orders=rows,
            total_outstanding=q2(total),
            orders_count=len(rows),
            buckets=[
                AgingBucketRead(
                    bucket=key,
                    orders_count=buckets[key][0],
                    outstanding=q2(buckets[key][1]),
                )
                for key, _ in _AGING_BUCKETS
            ],
            total_deposit_due=q2(total_deposit_due),
            deposit_shortfall=q2(deposit_shortfall),
            collection_rate_pct=(
                q2(total_collected / total_billed * 100)
                if total_billed > 0
                else Decimal("0")
            ),
        )
