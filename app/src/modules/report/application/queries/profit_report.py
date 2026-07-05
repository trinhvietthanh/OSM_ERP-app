from datetime import date, datetime, time, timedelta
from decimal import Decimal

from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.entities.order import Order
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderStatus
from src.modules.report.application.dto.report import (
    OrderProfitRead,
    ProfitReportRead,
    q2,
)
from src.modules.trip.domain.value_objects.trip import TripId

#: Orders that never generated revenue are excluded from profit.
_EXCLUDED = frozenset({OrderStatus.CANCELLED})


def _order_cost(order: Order) -> tuple[Decimal, bool]:
    """Actual spend on an order = Σ purchased_qty × actual_unit_cost.

    Returns (cost, complete): *complete* is False while any sold quantity has
    no recorded actual cost yet.
    """
    cost = Decimal("0")
    complete = True
    for line in order.lines:
        if line.actual_unit_cost is not None:
            cost += line.actual_unit_cost.amount * line.purchased_quantity
        if (
            line.purchased_quantity < line.quantity.value
            or line.actual_unit_cost is None
        ):
            complete = False
    return cost, complete


class ProfitReport:
    """Per-order profit (doanh thu − giá mua thực tế) with totals.

    Computed in the application layer over hydrated aggregates — shop-scale
    volumes (hundreds of orders) don't warrant SQL aggregation yet.
    """

    def __init__(
        self,
        orders: AbstractOrderRepository,
        customers: AbstractCustomerRepository,
    ) -> None:
        self._orders = orders
        self._customers = customers

    async def execute(
        self,
        organization_id: OrganizationId,
        date_from: date | None = None,
        date_to: date | None = None,
        trip_id: TripId | None = None,
    ) -> ProfitReportRead:
        orders = await self._orders.list(organization_id, trip_id=trip_id)
        names = {
            c.id_: c.name.value
            for c in await self._customers.list(organization_id, active_only=False)
        }

        rows: list[OrderProfitRead] = []
        total_revenue = Decimal("0")
        total_cost = Decimal("0")
        incomplete = 0

        for order in orders:
            if order.status in _EXCLUDED:
                continue
            created = order.created_at
            if date_from is not None and created < _day_start(date_from, created):
                continue
            if date_to is not None and created >= _day_end(date_to, created):
                continue

            revenue = order.total_amount
            cost, complete = _order_cost(order)
            profit = revenue - cost
            if not complete:
                incomplete += 1
            total_revenue += revenue
            total_cost += cost

            rows.append(
                OrderProfitRead(
                    order_id=order.id_.value,
                    tracking_code=order.tracking_code.value,
                    customer_name=names.get(order.customer_id, ""),
                    status=order.status.value,
                    trip_id=order.trip_id.value if order.trip_id else None,
                    revenue=q2(revenue),
                    cost=q2(cost),
                    profit=q2(profit),
                    margin_pct=(
                        q2(profit / revenue * 100) if revenue > 0 else None
                    ),
                    cost_complete=complete,
                    created_at=order.created_at,
                )
            )

        return ProfitReportRead(
            orders=rows,
            total_revenue=q2(total_revenue),
            total_cost=q2(total_cost),
            total_profit=q2(total_revenue - total_cost),
            orders_count=len(rows),
            orders_with_incomplete_cost=incomplete,
        )


def _day_start(day: date, like: datetime) -> datetime:
    return datetime.combine(day, time.min, tzinfo=like.tzinfo)


def _day_end(day: date, like: datetime) -> datetime:
    return datetime.combine(day + timedelta(days=1), time.min, tzinfo=like.tzinfo)
