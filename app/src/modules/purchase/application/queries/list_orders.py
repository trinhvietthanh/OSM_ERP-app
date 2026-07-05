from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.dto.order import OrderRead
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderStatus
from src.modules.trip.domain.value_objects.trip import TripId


class ListOrders:
    """List the tenant's orders with display customer names."""

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
        status: OrderStatus | None = None,
        customer_id: CustomerId | None = None,
        trip_id: TripId | None = None,
        unassigned: bool = False,
    ) -> list[OrderRead]:
        orders = await self._orders.list(
            organization_id,
            status=status,
            customer_id=customer_id,
            trip_id=trip_id,
            unassigned=unassigned,
        )
        # One pass over the customer book beats a query per order here —
        # shops have hundreds of customers, not millions.
        names = {
            c.id_: c.name.value
            for c in await self._customers.list(organization_id, active_only=False)
        }
        return [
            OrderRead.from_entity(o, customer_name=names.get(o.customer_id, ""))
            for o in orders
        ]
