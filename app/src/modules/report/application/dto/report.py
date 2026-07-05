from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel

_CENT = Decimal("0.01")


def q2(value: Decimal) -> Decimal:
    """Normalize money to 2 decimal places."""
    return value.quantize(_CENT)


class OrderProfitRead(BaseModel):
    """Profit line for one order: revenue vs actual purchase cost.

    ``cost_complete`` is False while some sold quantity still has no recorded
    actual cost — the profit shown is then a lower bound on spend.
    """

    order_id: UUID
    tracking_code: str
    customer_name: str
    status: str
    trip_id: UUID | None = None
    revenue: Decimal
    cost: Decimal
    profit: Decimal
    margin_pct: Decimal | None = None
    cost_complete: bool
    created_at: datetime


class ProfitReportRead(BaseModel):
    """Aggregate profit report over the selected orders."""

    orders: list[OrderProfitRead]
    total_revenue: Decimal
    total_cost: Decimal
    total_profit: Decimal
    orders_count: int
    orders_with_incomplete_cost: int


class ReceivableRead(BaseModel):
    """One order the customer still owes money on (công nợ)."""

    order_id: UUID
    tracking_code: str
    customer_id: UUID
    customer_name: str
    status: str
    total_amount: Decimal
    total_collected: Decimal
    remaining: Decimal
    created_at: datetime


class ReceivablesReportRead(BaseModel):
    """Outstanding balances across all open orders."""

    orders: list[ReceivableRead]
    total_outstanding: Decimal
    orders_count: int
