from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.dto.order import (
    ChangeOrderStatusInput,
    OrderRead,
)
from src.modules.purchase.application.exceptions import OrderNotFoundError
from src.modules.purchase.application.queries.get_order import resolve_customer_name
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderId, OrderStatus
from src.shared.domain.base import DomainError


class ChangeOrderStatus:
    """Advance one order through its lifecycle (validated transition)."""

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
        id_: OrderId,
        inp: ChangeOrderStatusInput,
    ) -> OrderRead:
        try:
            new_status = OrderStatus(inp.status)
        except ValueError as exc:
            raise DomainError(f"Unknown order status: {inp.status!r}.") from exc

        order = await self._orders.get(organization_id, id_)
        if order is None:
            raise OrderNotFoundError(id_.value)

        order.change_status(new_status)

        saved = await self._orders.save(order)
        if saved is None:
            raise OrderNotFoundError(id_.value)
        name = await resolve_customer_name(
            self._customers, organization_id, saved.customer_id
        )
        return OrderRead.from_entity(saved, customer_name=name)
