from decimal import Decimal

from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderStatus
from src.modules.report.application.dto.report import (
    ReceivableRead,
    ReceivablesReportRead,
    q2,
)


class ReceivablesReport:
    """Outstanding customer balances (công nợ): every non-cancelled order
    with remaining > 0, including delivered ones the customer still owes."""

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

        rows: list[ReceivableRead] = []
        total = Decimal("0")
        for order in orders:
            if order.status is OrderStatus.CANCELLED:
                continue
            remaining = order.remaining
            if remaining <= 0:
                continue
            total += remaining
            rows.append(
                ReceivableRead(
                    order_id=order.id_.value,
                    tracking_code=order.tracking_code.value,
                    customer_id=order.customer_id.value,
                    customer_name=names.get(order.customer_id, ""),
                    status=order.status.value,
                    total_amount=q2(order.total_amount),
                    total_collected=q2(order.total_collected),
                    remaining=q2(remaining),
                    created_at=order.created_at,
                )
            )

        rows.sort(key=lambda r: r.remaining, reverse=True)
        return ReceivablesReportRead(
            orders=rows,
            total_outstanding=q2(total),
            orders_count=len(rows),
        )
