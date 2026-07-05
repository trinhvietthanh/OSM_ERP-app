from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.dto.order import (
    CreateReceiptInput,
    OrderRead,
)
from src.modules.purchase.application.exceptions import OrderNotFoundError
from src.modules.purchase.application.queries.get_order import resolve_customer_name
from src.modules.purchase.domain.entities.order import PaymentReceipt
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import (
    OrderId,
    ReceiptKind,
    ReceiptMethod,
)
from src.shared.domain.base import DomainError
from src.shared.domain.money import Money


class AddReceipt:
    """Record a money collection (phiếu thu) on an order."""

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
        inp: CreateReceiptInput,
    ) -> OrderRead:
        try:
            method = ReceiptMethod(inp.method)
        except ValueError as exc:
            raise DomainError(f"Unknown receipt method: {inp.method!r}.") from exc
        try:
            kind = ReceiptKind(inp.kind)
        except ValueError as exc:
            raise DomainError(f"Unknown receipt kind: {inp.kind!r}.") from exc

        order = await self._orders.get(organization_id, id_)
        if order is None:
            raise OrderNotFoundError(id_.value)

        order.add_receipt(
            PaymentReceipt.create(
                amount=Money(amount=inp.amount),
                method=method,
                kind=kind,
                received_at=inp.received_at,
                note=inp.note,
            )
        )

        saved = await self._orders.save(order)
        if saved is None:
            raise OrderNotFoundError(id_.value)
        name = await resolve_customer_name(
            self._customers, organization_id, saved.customer_id
        )
        return OrderRead.from_entity(saved, customer_name=name)
