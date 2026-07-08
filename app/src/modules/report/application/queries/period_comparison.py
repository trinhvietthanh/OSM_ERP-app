from collections.abc import Sequence
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.entities.order import Order
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.report.application.dto.report import (
    PeriodComparisonRead,
    PeriodKpisRead,
    q2,
)
from src.modules.report.application.queries._shared import (
    EXCLUDED,
    in_period,
    order_cost,
)


class PeriodComparison:
    """KPIs for a period vs the one right before it (so sánh kỳ).

    Without an explicit range: current calendar month to date, compared to the
    full previous calendar month. With a range: the previous period is the
    same number of days immediately preceding ``date_from``. KPIs are over
    orders *created* in each period; the frontend derives the % deltas.
    """

    def __init__(self, orders: AbstractOrderRepository) -> None:
        self._orders = orders

    async def execute(
        self,
        organization_id: OrganizationId,
        date_from: date | None = None,
        date_to: date | None = None,
    ) -> PeriodComparisonRead:
        if date_from is None or date_to is None:
            today = datetime.now(UTC).date()
            date_from = today.replace(day=1)
            date_to = today
            prev_to = date_from - timedelta(days=1)
            prev_from = prev_to.replace(day=1)
        else:
            length = (date_to - date_from).days + 1
            prev_to = date_from - timedelta(days=1)
            prev_from = date_from - timedelta(days=length)

        orders = await self._orders.list(organization_id)
        return PeriodComparisonRead(
            current=_period_kpis(orders, date_from, date_to),
            previous=_period_kpis(orders, prev_from, prev_to),
        )


def _period_kpis(
    orders: Sequence[Order], date_from: date, date_to: date
) -> PeriodKpisRead:
    count = 0
    revenue = Decimal("0")
    collected = Decimal("0")
    cost = Decimal("0")

    for order in orders:
        if order.status in EXCLUDED:
            continue
        if not in_period(order.created_at, date_from, date_to):
            continue
        count += 1
        revenue += order.total_amount
        collected += order.total_collected
        spend, _complete = order_cost(order)
        cost += spend

    return PeriodKpisRead(
        date_from=date_from,
        date_to=date_to,
        orders_count=count,
        revenue=q2(revenue),
        collected=q2(collected),
        cost=q2(cost),
        profit=q2(revenue - cost),
    )
