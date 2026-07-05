from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.entities.order import (
    Order,
    OrderLine,
    PaymentReceipt,
)
from src.modules.purchase.domain.value_objects.order import (
    OrderId,
    OrderLineId,
    PaymentReceiptId,
    Quantity,
    TrackingCode,
)
from src.modules.purchase.infrastructure.models import (
    OrderLineModel,
    OrderModel,
    OrderReceiptModel,
)
from src.modules.trip.domain.value_objects.trip import TripId
from src.shared.domain.money import Money


# --- children ---


def line_model_to_entity(model: OrderLineModel) -> OrderLine:
    return OrderLine(
        id_=OrderLineId(value=model.id),
        product_id=ProductId(value=model.product_id),
        product_code=model.product_code,
        product_name=model.product_name,
        quantity=Quantity(value=model.quantity),
        unit_price=Money(amount=model.unit_price),
        unit_deposit=Money(amount=model.unit_deposit),
        purchased_quantity=model.purchased_quantity,
        actual_unit_cost=(
            Money(amount=model.actual_unit_cost)
            if model.actual_unit_cost is not None
            else None
        ),
        purchased_at=model.purchased_at,
    )


def line_entity_to_model(entity: OrderLine, order_id: OrderId) -> OrderLineModel:
    return OrderLineModel(
        id=entity.id_.value,
        order_id=order_id.value,
        product_id=entity.product_id.value,
        product_code=entity.product_code,
        product_name=entity.product_name,
        quantity=entity.quantity.value,
        unit_price=entity.unit_price.amount,
        unit_deposit=entity.unit_deposit.amount,
        purchased_quantity=entity.purchased_quantity,
        actual_unit_cost=(
            entity.actual_unit_cost.amount
            if entity.actual_unit_cost is not None
            else None
        ),
        purchased_at=entity.purchased_at,
    )


def apply_line_to_model(entity: OrderLine, model: OrderLineModel) -> None:
    """Copy mutable fields. Identity/product snapshot stay as created."""
    model.quantity = entity.quantity.value
    model.unit_price = entity.unit_price.amount
    model.unit_deposit = entity.unit_deposit.amount
    model.purchased_quantity = entity.purchased_quantity
    model.actual_unit_cost = (
        entity.actual_unit_cost.amount if entity.actual_unit_cost is not None else None
    )
    model.purchased_at = entity.purchased_at


def receipt_model_to_entity(model: OrderReceiptModel) -> PaymentReceipt:
    return PaymentReceipt(
        id_=PaymentReceiptId(value=model.id),
        amount=Money(amount=model.amount),
        method=model.method,
        kind=model.kind,
        received_at=model.received_at,
        note=model.note,
    )


def receipt_entity_to_model(
    entity: PaymentReceipt, order_id: OrderId
) -> OrderReceiptModel:
    return OrderReceiptModel(
        id=entity.id_.value,
        order_id=order_id.value,
        amount=entity.amount.amount,
        method=entity.method,
        kind=entity.kind,
        received_at=entity.received_at,
        note=entity.note,
    )


# --- aggregate root ---


def order_model_to_entity(model: OrderModel) -> Order:
    return Order(
        id_=OrderId(value=model.id),
        organization_id=OrganizationId(value=model.organization_id),
        customer_id=CustomerId(value=model.customer_id),
        tracking_code=TrackingCode(value=model.tracking_code),
        lines=[line_model_to_entity(m) for m in model.lines],
        receipts=[receipt_model_to_entity(m) for m in model.receipts],
        status=model.status,
        is_separate=model.is_separate,
        trip_id=TripId(value=model.trip_id) if model.trip_id is not None else None,
        note=model.note,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def order_entity_to_model(entity: Order) -> OrderModel:
    return OrderModel(
        id=entity.id_.value,
        organization_id=entity.organization_id.value,
        customer_id=entity.customer_id.value,
        trip_id=entity.trip_id.value if entity.trip_id is not None else None,
        tracking_code=entity.tracking_code.value,
        status=entity.status,
        is_separate=entity.is_separate,
        note=entity.note,
        lines=[line_entity_to_model(line, entity.id_) for line in entity.lines],
        receipts=[receipt_entity_to_model(r, entity.id_) for r in entity.receipts],
    )


def apply_order_to_model(entity: Order, model: OrderModel) -> None:
    """Reconcile the aggregate onto the loaded model, children included.

    Root scalars are copied; child collections are diffed by id — removed
    children are deleted (via delete-orphan cascade), new ones inserted,
    existing ones updated in place.
    """
    model.customer_id = entity.customer_id.value
    model.trip_id = entity.trip_id.value if entity.trip_id is not None else None
    model.status = entity.status
    model.is_separate = entity.is_separate
    model.note = entity.note

    # lines
    line_models = {m.id: m for m in model.lines}
    kept_lines = []
    for line in entity.lines:
        existing = line_models.get(line.id_.value)
        if existing is not None:
            apply_line_to_model(line, existing)
            kept_lines.append(existing)
        else:
            kept_lines.append(line_entity_to_model(line, entity.id_))
    model.lines[:] = kept_lines

    # receipts (immutable rows: add/remove only)
    receipt_models = {m.id: m for m in model.receipts}
    kept_receipts = []
    for receipt in entity.receipts:
        existing = receipt_models.get(receipt.id_.value)
        kept_receipts.append(
            existing
            if existing is not None
            else receipt_entity_to_model(receipt, entity.id_)
        )
    model.receipts[:] = kept_receipts
