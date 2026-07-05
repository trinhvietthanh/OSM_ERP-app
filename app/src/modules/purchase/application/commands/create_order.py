from sqlalchemy.exc import IntegrityError

from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.customer.application.exceptions import CustomerNotFoundError
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.application.dto.order import (
    CreateOrderInput,
    OrderRead,
)
from src.modules.purchase.application.exceptions import (
    TrackingCodeGenerationError,
)
from src.modules.purchase.application.line_builder import build_lines
from src.modules.purchase.domain.entities.order import Order, PaymentReceipt
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.domain.value_objects.order import (
    OrderStatus,
    ReceiptMethod,
    TrackingCode,
)
from src.shared.domain.money import Money

_MAX_CODE_ATTEMPTS = 5


class CreateOrder:
    """Create a new order: validate customer and products, snapshot product
    names, generate a globally-unique tracking code, and optionally record the
    deposit collected at order time (which confirms the order)."""

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
        self, organization_id: OrganizationId, inp: CreateOrderInput
    ) -> OrderRead:
        customer_id = CustomerId(value=inp.customer_id)
        customer = await self._customers.get(organization_id, customer_id)
        if customer is None:
            raise CustomerNotFoundError(inp.customer_id)

        lines = await build_lines(self._products, organization_id, inp.lines)

        # Unique-code loop: pre-check, then rely on the DB unique constraint
        # as the race-condition backstop (retry with a fresh code).
        for _ in range(_MAX_CODE_ATTEMPTS):
            code = TrackingCode.generate()
            if await self._orders.get_by_tracking_code(code) is not None:
                continue
            order = Order.create(
                organization_id=organization_id,
                customer_id=customer_id,
                tracking_code=code,
                lines=lines,
                is_separate=inp.is_separate,
                note=inp.note,
            )
            if inp.initial_receipt is not None:
                order.add_receipt(
                    PaymentReceipt.create(
                        amount=Money(amount=inp.initial_receipt.amount),
                        method=ReceiptMethod(inp.initial_receipt.method),
                        received_at=inp.initial_receipt.received_at,
                        note=inp.initial_receipt.note,
                    )
                )
                order.change_status(OrderStatus.CONFIRMED)
            try:
                saved = await self._orders.add(order)
            except IntegrityError as exc:
                # Lost a code race after the pre-check (practically
                # unreachable). The session is now invalid, so surface a
                # retryable error instead of flushing again on it.
                raise TrackingCodeGenerationError() from exc
            return OrderRead.from_entity(saved, customer_name=customer.name.value)
        raise TrackingCodeGenerationError()
