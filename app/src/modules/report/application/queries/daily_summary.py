from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from decimal import Decimal

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderStatus
from src.modules.report.application.dto.report import (
    DailyBucketRead,
    DailySummaryRead,
    q2,
)
from src.modules.report.application.queries._shared import (
    EXCLUDED,
    in_period,
    order_cost,
)
#: An order counts as "chốt" once it reaches CONFIRMED or any later stage.
_CONFIRMED_OR_LATER = frozenset(
    {
        OrderStatus.CONFIRMED,
        OrderStatus.PURCHASING,
        OrderStatus.PURCHASED,
        OrderStatus.ARRIVED,
        OrderStatus.DELIVERED,
    }
)


@dataclass
class _Day:
    """Mutable per-day accumulator."""

    orders: int = 0
    confirmed: int = 0
    revenue: Decimal = field(default_factory=lambda: Decimal("0"))
    collected: Decimal = field(default_factory=lambda: Decimal("0"))
    cost: Decimal = field(default_factory=lambda: Decimal("0"))


class DailySummary:
    """Orders grouped by creation date — the shop's daily pulse (đơn theo ngày).

    Grouped by ``created_at`` (the only reliable per-order date — there is no
    status-history yet, so the "chốt" date itself isn't recorded). For each day:
    how many orders were taken, how many are "đã chốt", revenue, cash collected,
    and actual purchase cost. Computed in the application layer over hydrated
    aggregates.
    """

    def __init__(self, orders: AbstractOrderRepository) -> None:
        self._orders = orders

    async def execute(
        self,
        organization_id: OrganizationId,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> DailySummaryRead:
        orders = await self._orders.list(organization_id)

        buckets: dict[date, _Day] = defaultdict(_Day)
        totals = _Day()

        for order in orders:
            if order.status in EXCLUDED:
                continue
            if not in_period(order.created_at, date_from, date_to):
                continue

            cost, _complete = order_cost(order)
            day = buckets[order.created_at.date()]
            day.orders += 1
            if order.status in _CONFIRMED_OR_LATER:
                day.confirmed += 1
                totals.confirmed += 1
            day.revenue += order.total_amount
            day.collected += order.total_collected
            day.cost += cost

            totals.orders += 1
            totals.revenue += order.total_amount
            totals.collected += order.total_collected
            totals.cost += cost

        days = [
            DailyBucketRead(
                date=day,
                orders_count=b.orders,
                confirmed_count=b.confirmed,
                revenue=q2(b.revenue),
                collected=q2(b.collected),
                cost=q2(b.cost),
            )
            for day, b in sorted(buckets.items())
        ]
        return DailySummaryRead(
            days=days,
            orders_count=totals.orders,
            confirmed_count=totals.confirmed,
            revenue=q2(totals.revenue),
            collected=q2(totals.collected),
            cost=q2(totals.cost),
        )
