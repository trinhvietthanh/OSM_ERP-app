from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from src.modules.purchase.domain.entities.order import (
    Order,
    OrderLine,
    PaymentReceipt,
)

_CENT = Decimal("0.01")


def _q2(value: Decimal) -> Decimal:
    """Normalize money to 2 decimal places (derived sums lose the DB scale)."""
    return value.quantize(_CENT)


class OrderLineInput(BaseModel):
    """One product line when creating/replacing order lines.

    Prices are free-form (nhập tự do): the seller types them, they are not
    resolved from any campaign. Money values are decimal strings/numbers.
    """

    product_id: UUID
    quantity: int
    unit_price: Decimal
    unit_deposit: Decimal = Decimal("0")


class CreateReceiptInput(BaseModel):
    """One money movement (phiếu thu / phiếu hoàn)."""

    amount: Decimal
    method: str = "cash"  # cash | bank_transfer | other
    kind: str = "collection"  # collection | refund
    received_at: datetime | None = None
    note: str = ""


class CreateOrderInput(BaseModel):
    """Payload for the CreateOrder command.

    ``initial_receipt`` records the deposit collected at order time in the
    same transaction (and confirms the order).
    """

    customer_id: UUID
    lines: list[OrderLineInput]
    is_separate: bool = False
    note: str = ""
    initial_receipt: CreateReceiptInput | None = None


class UpdateOrderInput(BaseModel):
    """Partial payload for the UpdateOrder command.

    ``lines`` replacement is only allowed while the order is PENDING.
    """

    note: str | None = None
    is_separate: bool | None = None
    lines: list[OrderLineInput] | None = None


class ChangeOrderStatusInput(BaseModel):
    """Payload for the ChangeOrderStatus command."""

    status: str  # pending | confirmed | purchasing | purchased | arrived | delivered | cancelled


class RecordLinePurchaseInput(BaseModel):
    """Buying progress on one line (admin enters the shopper's actuals)."""

    purchased_quantity: int
    actual_unit_cost: Decimal | None = None


class OrderLineRead(BaseModel):
    """Read model for one order line."""

    id: UUID
    product_id: UUID
    product_code: str
    product_name: str
    quantity: int
    unit_price: Decimal
    unit_deposit: Decimal
    line_total: Decimal
    purchased_quantity: int
    actual_unit_cost: Decimal | None = None
    purchased_at: datetime | None = None

    @classmethod
    def from_entity(cls, line: OrderLine) -> Self:
        return cls(
            id=line.id_.value,
            product_id=line.product_id.value,
            product_code=line.product_code,
            product_name=line.product_name,
            quantity=line.quantity.value,
            unit_price=_q2(line.unit_price.amount),
            unit_deposit=_q2(line.unit_deposit.amount),
            line_total=_q2(line.line_total),
            purchased_quantity=line.purchased_quantity,
            actual_unit_cost=(
                _q2(line.actual_unit_cost.amount)
                if line.actual_unit_cost is not None
                else None
            ),
            purchased_at=line.purchased_at,
        )


class ReceiptRead(BaseModel):
    """Read model for one payment receipt."""

    id: UUID
    amount: Decimal
    method: str
    kind: str
    received_at: datetime
    note: str

    @classmethod
    def from_entity(cls, receipt: PaymentReceipt) -> Self:
        return cls(
            id=receipt.id_.value,
            amount=_q2(receipt.amount.amount),
            method=receipt.method.value,
            kind=receipt.kind.value,
            received_at=receipt.received_at,
            note=receipt.note,
        )


class OrderRead(BaseModel):
    """Read model returned by order commands and queries.

    ``customer_name`` is joined in from the customer module for display.
    """

    id: UUID
    organization_id: UUID
    customer_id: UUID
    customer_name: str
    tracking_code: str
    status: str
    is_separate: bool
    trip_id: UUID | None = None
    note: str
    lines: list[OrderLineRead]
    receipts: list[ReceiptRead]
    total_amount: Decimal
    deposit_due: Decimal
    total_collected: Decimal
    total_refunded: Decimal
    remaining: Decimal
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, order: Order, customer_name: str = "") -> Self:
        return cls(
            id=order.id_.value,
            organization_id=order.organization_id.value,
            customer_id=order.customer_id.value,
            customer_name=customer_name,
            tracking_code=order.tracking_code.value,
            status=order.status.value,
            is_separate=order.is_separate,
            trip_id=order.trip_id.value if order.trip_id is not None else None,
            note=order.note,
            lines=[OrderLineRead.from_entity(line) for line in order.lines],
            receipts=[ReceiptRead.from_entity(r) for r in order.receipts],
            total_amount=_q2(order.total_amount),
            deposit_due=_q2(order.deposit_due),
            total_collected=_q2(order.total_collected),
            total_refunded=_q2(order.total_refunded),
            remaining=_q2(order.remaining),
            created_at=order.created_at,
            updated_at=order.updated_at,
        )
