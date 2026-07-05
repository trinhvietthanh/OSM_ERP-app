from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.exceptions import (
    OrderNotFoundError,
    ReceiptNotFoundError,
)
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import (
    OrderId,
    PaymentReceiptId,
)


class RemoveReceipt:
    """Delete a receipt from an order (correction path)."""

    def __init__(self, orders: AbstractOrderRepository) -> None:
        self._orders = orders

    async def execute(
        self,
        organization_id: OrganizationId,
        id_: OrderId,
        receipt_id: PaymentReceiptId,
    ) -> None:
        order = await self._orders.get(organization_id, id_)
        if order is None:
            raise OrderNotFoundError(id_.value)
        if not order.remove_receipt(receipt_id):
            raise ReceiptNotFoundError(receipt_id.value)
        if await self._orders.save(order) is None:
            raise OrderNotFoundError(id_.value)
