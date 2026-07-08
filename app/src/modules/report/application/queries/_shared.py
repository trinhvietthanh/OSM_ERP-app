"""Helpers shared by the report queries.

All reports iterate hydrated Order aggregates in the application layer —
shop-scale volumes (hundreds of orders) don't warrant SQL aggregation yet.
"""

from datetime import date, datetime, time, timedelta
from decimal import Decimal

from src.modules.purchase.domain.entities.order import Order
from src.modules.purchase.domain.value_objects.order import OrderStatus

#: Orders that never generated revenue are excluded from money figures.
EXCLUDED = frozenset({OrderStatus.CANCELLED})


def order_cost(order: Order) -> tuple[Decimal, bool]:
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


def day_start(day: date, like: datetime) -> datetime:
    return datetime.combine(day, time.min, tzinfo=like.tzinfo)


def day_end(day: date, like: datetime) -> datetime:
    return datetime.combine(day + timedelta(days=1), time.min, tzinfo=like.tzinfo)


def in_period(
    moment: datetime,
    date_from: date | None,
    date_to: date | None,
) -> bool:
    """True when *moment* falls within [date_from, date_to) (day bounds)."""
    if date_from is not None and moment < day_start(date_from, moment):
        return False
    if date_to is not None and moment >= day_end(date_to, moment):
        return False
    return True
