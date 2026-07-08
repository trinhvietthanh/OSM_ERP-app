from dataclasses import dataclass, field
from datetime import date, datetime
from decimal import Decimal

from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.report.application.dto.report import (
    CustomerMetricRead,
    CustomerReportRead,
    q2,
)
from src.modules.report.application.queries._shared import EXCLUDED, in_period


@dataclass
class _Customer:
    """Mutable per-customer accumulator over in-period orders."""

    orders: int = 0
    revenue: Decimal = field(default_factory=lambda: Decimal("0"))
    collected: Decimal = field(default_factory=lambda: Decimal("0"))
    outstanding: Decimal = field(default_factory=lambda: Decimal("0"))
    last_order_at: datetime | None = None


class CustomerReport:
    """Top customers by revenue in a period (top khách hàng).

    ``is_new`` marks customers whose first-ever order falls inside the period
    — without a date filter every listed customer is trivially "new", so the
    new/returning split is only meaningful when a range is given.
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
    ) -> CustomerReportRead:
        orders = await self._orders.list(organization_id)
        customers = {
            c.id_: c
            for c in await self._customers.list(organization_id, active_only=False)
        }

        earliest: dict[CustomerId, datetime] = {}
        acc: dict[CustomerId, _Customer] = {}

        for order in orders:
            if order.status in EXCLUDED:
                continue
            first = earliest.get(order.customer_id)
            if first is None or order.created_at < first:
                earliest[order.customer_id] = order.created_at

            if not in_period(order.created_at, date_from, date_to):
                continue
            row = acc.setdefault(order.customer_id, _Customer())
            row.orders += 1
            row.revenue += order.total_amount
            row.collected += order.total_collected
            remaining = order.remaining
            if remaining > 0:
                row.outstanding += remaining
            if row.last_order_at is None or order.created_at > row.last_order_at:
                row.last_order_at = order.created_at

        rows: list[CustomerMetricRead] = []
        new_count = 0
        for customer_id, row in acc.items():
            customer = customers.get(customer_id)
            is_new = in_period(earliest[customer_id], date_from, date_to)
            if is_new:
                new_count += 1
            rows.append(
                CustomerMetricRead(
                    customer_id=customer_id.value,
                    customer_name=(
                        customer.name.value if customer is not None else ""
                    ),
                    phone=(
                        customer.phone.value
                        if customer is not None and customer.phone is not None
                        else ""
                    ),
                    orders_count=row.orders,
                    revenue=q2(row.revenue),
                    collected=q2(row.collected),
                    outstanding=q2(row.outstanding),
                    avg_order_value=q2(row.revenue / row.orders),
                    last_order_at=row.last_order_at,
                    is_new=is_new,
                )
            )
        rows.sort(key=lambda r: r.revenue, reverse=True)

        return CustomerReportRead(
            customers=rows,
            customers_count=len(rows),
            new_customers_count=new_count,
            returning_customers_count=len(rows) - new_count,
            total_revenue=q2(sum((r.revenue for r in rows), Decimal("0"))),
            total_outstanding=q2(
                sum((r.outstanding for r in rows), Decimal("0"))
            ),
        )
