from datetime import UTC, date, datetime
from decimal import Decimal

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderStatus
from src.modules.report.application.dto.report import (
    OperationsReportRead,
    StuckStatusRead,
    q2,
)
from src.modules.report.application.queries._shared import in_period

#: Non-terminal stages where an order can silently sit and rot.
_STUCK_TRACKED = (
    OrderStatus.PENDING,
    OrderStatus.CONFIRMED,
    OrderStatus.PURCHASING,
    OrderStatus.PURCHASED,
    OrderStatus.ARRIVED,
)
#: Orders eligible to be consolidated into a buying trip (gom đơn).
_ASSIGNABLE = frozenset({OrderStatus.PENDING, OrderStatus.CONFIRMED})


class OperationsReport:
    """Operational health (chỉ số vận hành).

    Rates (cancellation, purchase completion) are computed over orders
    *created* in the period. Stuck orders are a current-state snapshot —
    non-terminal orders untouched for more than ``stale_days`` days — and
    ignore the date filter, as does ``unassigned_count``. True cycle-time
    (created → delivered duration) needs per-status timestamps and is
    deferred until those exist.
    """

    def __init__(self, orders: AbstractOrderRepository) -> None:
        self._orders = orders

    async def execute(
        self,
        organization_id: OrganizationId,
        date_from: date | None = None,
        date_to: date | None = None,
        stale_days: int = 7,
    ) -> OperationsReportRead:
        orders = await self._orders.list(organization_id)
        now = datetime.now(UTC)

        total = 0
        cancelled = 0
        ordered_qty = 0
        purchased_qty = 0
        unassigned = 0
        stuck: dict[OrderStatus, list] = {}  # [count, oldest_days, amount]

        for order in orders:
            if order.status in _STUCK_TRACKED:
                age_days = (now - order.updated_at).days
                if age_days > stale_days:
                    bucket = stuck.setdefault(order.status, [0, 0, Decimal("0")])
                    bucket[0] += 1
                    bucket[1] = max(bucket[1], age_days)
                    bucket[2] += order.total_amount

            if (
                order.trip_id is None
                and not order.is_separate
                and order.status in _ASSIGNABLE
            ):
                unassigned += 1

            if not in_period(order.created_at, date_from, date_to):
                continue
            total += 1
            if order.status is OrderStatus.CANCELLED:
                cancelled += 1
                continue
            for line in order.lines:
                ordered_qty += line.quantity.value
                purchased_qty += line.purchased_quantity

        return OperationsReportRead(
            orders_count=total,
            cancelled_count=cancelled,
            cancellation_rate_pct=(
                q2(Decimal(cancelled) / Decimal(total) * 100)
                if total > 0
                else Decimal("0")
            ),
            purchase_completion_pct=(
                q2(Decimal(purchased_qty) / Decimal(ordered_qty) * 100)
                if ordered_qty > 0
                else Decimal("0")
            ),
            unassigned_count=unassigned,
            stale_days=stale_days,
            stuck=[
                StuckStatusRead(
                    status=status.value,
                    count=stuck[status][0],
                    oldest_days=stuck[status][1],
                    total_amount=q2(stuck[status][2]),
                )
                for status in _STUCK_TRACKED
                if status in stuck
            ],
        )
