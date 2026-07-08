from collections import defaultdict
from decimal import Decimal

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderStatus
from src.modules.report.application.dto.report import (
    OverviewReportRead,
    StatusCountRead,
    q2,
)
from src.modules.report.application.queries._shared import order_cost

#: Display order for the pipeline funnel (pending → delivered, then cancelled).
_STATUS_ORDER = (
    OrderStatus.PENDING,
    OrderStatus.CONFIRMED,
    OrderStatus.PURCHASING,
    OrderStatus.PURCHASED,
    OrderStatus.ARRIVED,
    OrderStatus.DELIVERED,
    OrderStatus.CANCELLED,
)
#: Orders eligible to be consolidated into a buying trip (gom đơn).
_ASSIGNABLE = frozenset({OrderStatus.PENDING, OrderStatus.CONFIRMED})


class OverviewReport:
    """Snapshot dashboard for a pre-sale shop owner.

    Current-state KPIs (no date filter): the order pipeline funnel by status,
    revenue / cash held / debt / deposits owed / spend / profit across active
    orders, and how many orders still need consolidating into a trip.
    """

    def __init__(self, orders: AbstractOrderRepository) -> None:
        self._orders = orders

    async def execute(
        self, organization_id: OrganizationId
    ) -> OverviewReportRead:
        orders = await self._orders.list(organization_id)

        counts: dict[OrderStatus, list] = defaultdict(
            lambda: [0, Decimal("0")]  # [count, total_amount]
        )
        total_revenue = Decimal("0")
        total_collected = Decimal("0")
        total_outstanding = Decimal("0")
        total_deposit_due = Decimal("0")
        total_cost = Decimal("0")
        unassigned = 0

        for order in orders:
            bucket = counts[order.status]
            bucket[0] += 1
            bucket[1] += order.total_amount

            if order.status is OrderStatus.CANCELLED:
                continue

            total_revenue += order.total_amount
            total_collected += order.total_collected
            total_deposit_due += order.deposit_due
            remaining = order.remaining
            if remaining > 0:
                total_outstanding += remaining
            cost, _complete = order_cost(order)
            total_cost += cost

            if (
                order.trip_id is None
                and not order.is_separate
                and order.status in _ASSIGNABLE
            ):
                unassigned += 1

        status_breakdown = [
            StatusCountRead(
                status=status.value,
                count=counts[status][0],
                total_amount=q2(counts[status][1]),
            )
            for status in _STATUS_ORDER
            if status in counts
        ]
        return OverviewReportRead(
            status_breakdown=status_breakdown,
            orders_count=sum(b[0] for b in counts.values()),
            total_revenue=q2(total_revenue),
            total_collected=q2(total_collected),
            total_outstanding=q2(total_outstanding),
            total_deposit_due=q2(total_deposit_due),
            total_cost=q2(total_cost),
            total_profit=q2(total_revenue - total_cost),
            unassigned_count=unassigned,
        )
