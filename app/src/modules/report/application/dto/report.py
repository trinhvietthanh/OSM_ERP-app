from datetime import date, datetime
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
    """One order the customer still owes money on (công nợ).

    ``aging_bucket`` groups the debt by order age; ``deposit_covered`` is
    False while collections don't yet cover the agreed deposit (thiếu cọc).
    """

    order_id: UUID
    tracking_code: str
    customer_id: UUID
    customer_name: str
    status: str
    total_amount: Decimal
    total_collected: Decimal
    remaining: Decimal
    created_at: datetime
    age_days: int
    aging_bucket: str
    deposit_due: Decimal
    deposit_covered: bool


class AgingBucketRead(BaseModel):
    """Outstanding debt in one age bracket (all 4 brackets always emitted)."""

    bucket: str
    orders_count: int
    outstanding: Decimal


class ReceivablesReportRead(BaseModel):
    """Outstanding balances across all open orders.

    ``collection_rate_pct`` is collected / billed over the owing orders only;
    ``deposit_shortfall`` sums how much agreed deposit is still uncollected.
    """

    orders: list[ReceivableRead]
    total_outstanding: Decimal
    orders_count: int
    buckets: list[AgingBucketRead]
    total_deposit_due: Decimal
    deposit_shortfall: Decimal
    collection_rate_pct: Decimal


class DailyBucketRead(BaseModel):
    """One day in the daily order summary (grouped by order creation date).

    ``confirmed_count`` is the number of that day's orders that have been
    "chốt" — i.e. reached CONFIRMED or a later stage (not pending/cancelled).
    """

    date: date
    orders_count: int
    confirmed_count: int
    revenue: Decimal
    collected: Decimal
    cost: Decimal


class DailySummaryRead(BaseModel):
    """Daily order pulse over a date range, plus range totals."""

    days: list[DailyBucketRead]
    orders_count: int
    confirmed_count: int
    revenue: Decimal
    collected: Decimal
    cost: Decimal


class CashFlowReportRead(BaseModel):
    """Money in vs money out over a period.

    ``cash_in`` is customer collections (deposits + payments); ``cash_out`` is
    the actual cost of goods bought (recorded per line at purchase time);
    ``refunded`` is money returned to customers. ``pending_purchase_cost`` is
    the estimated spend left on goods ordered but not yet bought.
    """

    cash_in: Decimal
    cash_out: Decimal
    refunded: Decimal
    net: Decimal
    pending_purchase_cost: Decimal


class StatusCountRead(BaseModel):
    """How many orders sit in one lifecycle stage, and their total value."""

    status: str
    count: int
    total_amount: Decimal


class OverviewReportRead(BaseModel):
    """Snapshot dashboard for a pre-sale shop owner: pipeline funnel, money
    held, debt, deposits still owed, spend and profit."""

    status_breakdown: list[StatusCountRead]
    orders_count: int
    total_revenue: Decimal
    total_collected: Decimal
    total_outstanding: Decimal
    total_deposit_due: Decimal
    total_cost: Decimal
    total_profit: Decimal
    unassigned_count: int


class TripPnlRead(BaseModel):
    """P&L for one buying trip across its (non-cancelled) orders.

    ``purchase_progress_pct`` is bought quantity over ordered quantity;
    ``cost_complete`` is False while any line lacks a recorded actual cost.
    """

    trip_id: UUID
    trip_code: str
    trip_name: str
    status: str
    shopper_name: str
    departure_date: date | None = None
    arrival_date: date | None = None
    orders_count: int
    revenue: Decimal
    cost: Decimal
    profit: Decimal
    margin_pct: Decimal | None = None
    collected: Decimal
    outstanding: Decimal
    total_quantity: int
    purchased_quantity: int
    purchase_progress_pct: Decimal
    cost_complete: bool


class TripReportRead(BaseModel):
    """P&L per trip (lãi/lỗ theo chuyến hàng), newest trips first."""

    trips: list[TripPnlRead]
    trips_count: int
    total_revenue: Decimal
    total_cost: Decimal
    total_profit: Decimal


class ProductMetricRead(BaseModel):
    """Sales and margin for one product (grouped by product_code snapshot)."""

    product_id: UUID
    product_code: str
    product_name: str
    orders_count: int
    quantity_sold: int
    purchased_quantity: int
    revenue: Decimal
    cost: Decimal
    profit: Decimal
    margin_pct: Decimal | None = None
    cost_complete: bool


class ProductReportRead(BaseModel):
    """Best sellers over a period, sorted by revenue."""

    products: list[ProductMetricRead]
    products_count: int
    total_quantity: int
    total_revenue: Decimal
    total_cost: Decimal
    total_profit: Decimal


class CustomerMetricRead(BaseModel):
    """Buying activity of one customer within the period.

    ``is_new`` — the customer's first-ever order falls inside the period.
    """

    customer_id: UUID
    customer_name: str
    phone: str
    orders_count: int
    revenue: Decimal
    collected: Decimal
    outstanding: Decimal
    avg_order_value: Decimal
    last_order_at: datetime
    is_new: bool


class CustomerReportRead(BaseModel):
    """Top customers over a period, sorted by revenue."""

    customers: list[CustomerMetricRead]
    customers_count: int
    new_customers_count: int
    returning_customers_count: int
    total_revenue: Decimal
    total_outstanding: Decimal


class StuckStatusRead(BaseModel):
    """Orders sitting untouched in one lifecycle stage past the threshold."""

    status: str
    count: int
    oldest_days: int
    total_amount: Decimal


class OperationsReportRead(BaseModel):
    """Operational health: cancellation / purchase-completion rates over the
    period, plus current stuck and unassigned orders (snapshot)."""

    orders_count: int
    cancelled_count: int
    cancellation_rate_pct: Decimal
    purchase_completion_pct: Decimal
    unassigned_count: int
    stale_days: int
    stuck: list[StuckStatusRead]


class PeriodKpisRead(BaseModel):
    """Core KPIs over orders created in one period."""

    date_from: date
    date_to: date
    orders_count: int
    revenue: Decimal
    collected: Decimal
    cost: Decimal
    profit: Decimal


class PeriodComparisonRead(BaseModel):
    """Current period vs the period immediately before it (same length)."""

    current: PeriodKpisRead
    previous: PeriodKpisRead
