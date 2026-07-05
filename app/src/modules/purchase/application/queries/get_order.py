from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.dto.order import OrderRead
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderId


async def resolve_customer_name(
    customers: AbstractCustomerRepository,
    organization_id: OrganizationId,
    customer_id: CustomerId,
) -> str:
    """Display-name lookup for OrderRead; empty string if the customer is gone."""
    customer = await customers.get(organization_id, customer_id)
    return customer.name.value if customer is not None else ""


class GetOrder:
    """Fetch a single order (lines + receipts + customer name)."""

    def __init__(
        self,
        orders: AbstractOrderRepository,
        customers: AbstractCustomerRepository,
    ) -> None:
        self._orders = orders
        self._customers = customers

    async def execute(
        self, organization_id: OrganizationId, id_: OrderId
    ) -> OrderRead | None:
        order = await self._orders.get(organization_id, id_)
        if order is None:
            return None
        name = await resolve_customer_name(
            self._customers, organization_id, order.customer_id
        )
        return OrderRead.from_entity(order, customer_name=name)
