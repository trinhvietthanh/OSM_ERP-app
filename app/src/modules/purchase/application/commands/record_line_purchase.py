from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.dto.order import (
    OrderRead,
    RecordLinePurchaseInput,
)
from src.modules.purchase.application.exceptions import (
    OrderLineNotFoundError,
    OrderNotFoundError,
)
from src.modules.purchase.application.queries.get_order import resolve_customer_name
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderId, OrderLineId
from src.shared.domain.money import Money


class RecordLinePurchase:
    """Record buying progress (purchased quantity + actual cost) on one line.

    Works for orders in a trip and for solo ("giao riêng") orders alike; the
    order auto-advances to PURCHASED once every line is fully bought.
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
        id_: OrderId,
        line_id: OrderLineId,
        inp: RecordLinePurchaseInput,
    ) -> OrderRead:
        order = await self._orders.get(organization_id, id_)
        if order is None:
            raise OrderNotFoundError(id_.value)
        if order.find_line(line_id) is None:
            raise OrderLineNotFoundError(line_id.value)

        order.record_line_purchase(
            line_id,
            inp.purchased_quantity,
            Money(amount=inp.actual_unit_cost)
            if inp.actual_unit_cost is not None
            else None,
        )

        saved = await self._orders.save(order)
        if saved is None:
            raise OrderNotFoundError(id_.value)
        name = await resolve_customer_name(
            self._customers, organization_id, saved.customer_id
        )
        return OrderRead.from_entity(saved, customer_name=name)
