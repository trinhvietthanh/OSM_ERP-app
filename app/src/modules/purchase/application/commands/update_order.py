from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.dto.order import OrderRead, UpdateOrderInput
from src.modules.purchase.application.exceptions import OrderNotFoundError
from src.modules.purchase.application.line_builder import build_lines
from src.modules.purchase.application.queries.get_order import resolve_customer_name
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import OrderId


class UpdateOrder:
    """Apply a partial update (note / giao riêng / line replacement while
    pending) to an existing order."""

    def __init__(
        self,
        orders: AbstractOrderRepository,
        customers: AbstractCustomerRepository,
        products: AbstractProductRepository,
    ) -> None:
        self._orders = orders
        self._customers = customers
        self._products = products

    async def execute(
        self, organization_id: OrganizationId, id_: OrderId, inp: UpdateOrderInput
    ) -> OrderRead:
        order = await self._orders.get(organization_id, id_)
        if order is None:
            raise OrderNotFoundError(id_.value)

        if inp.note is not None:
            order.change_note(inp.note)
        if inp.is_separate is not None:
            order.set_separate(inp.is_separate)
        if inp.lines is not None:
            order.replace_lines(
                await build_lines(self._products, organization_id, inp.lines)
            )

        saved = await self._orders.save(order)
        if saved is None:
            raise OrderNotFoundError(id_.value)
        name = await resolve_customer_name(
            self._customers, organization_id, saved.customer_id
        )
        return OrderRead.from_entity(saved, customer_name=name)
