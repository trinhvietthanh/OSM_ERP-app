from datetime import UTC, datetime
from decimal import Decimal
from typing import Self

from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.customer.domain.value_objects.customer import CustomerId
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.purchase.domain.value_objects.order import (
    ALLOWED_ORDER_TRANSITIONS,
    OrderId,
    OrderLineId,
    OrderStatus,
    PaymentReceiptId,
    Quantity,
    ReceiptKind,
    ReceiptMethod,
    TrackingCode,
)
from src.modules.trip.domain.value_objects.trip import TripId
from src.shared.domain.base import DomainError, Entity
from src.shared.domain.money import Money


class OrderLine(Entity[OrderLineId]):
    """A product line inside an Order.

    ``product_code``/``product_name`` are snapshots taken at order time —
    the order must keep showing what was sold even if the catalog product is
    later renamed. ``unit_price``/``unit_deposit`` are free-form (entered by
    the seller, not bound to any campaign). Purchase progress
    (``purchased_quantity``, ``actual_unit_cost``) is recorded during the trip
    and feeds the future P&L report.
    """

    def __init__(
        self,
        *,
        id_: OrderLineId,
        product_id: ProductId,
        product_code: str,
        product_name: str,
        quantity: Quantity,
        unit_price: Money,
        unit_deposit: Money,
        purchased_quantity: int = 0,
        actual_unit_cost: Money | None = None,
        purchased_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        self._product_id = product_id
        self._product_code = product_code
        self._product_name = product_name
        self._quantity = quantity
        self._unit_price = unit_price
        self._unit_deposit = unit_deposit
        self._purchased_quantity = purchased_quantity
        self._actual_unit_cost = actual_unit_cost
        self._purchased_at = purchased_at

    @classmethod
    def create(
        cls,
        *,
        product_id: ProductId,
        product_code: str,
        product_name: str,
        quantity: Quantity,
        unit_price: Money,
        unit_deposit: Money,
    ) -> Self:
        return cls(
            id_=OrderLineId.generate(),
            product_id=product_id,
            product_code=product_code,
            product_name=product_name,
            quantity=quantity,
            unit_price=unit_price,
            unit_deposit=unit_deposit,
        )

    @property
    def product_id(self) -> ProductId:
        return self._product_id

    @property
    def product_code(self) -> str:
        return self._product_code

    @property
    def product_name(self) -> str:
        return self._product_name

    @property
    def quantity(self) -> Quantity:
        return self._quantity

    @property
    def unit_price(self) -> Money:
        return self._unit_price

    @property
    def unit_deposit(self) -> Money:
        return self._unit_deposit

    @property
    def purchased_quantity(self) -> int:
        return self._purchased_quantity

    @property
    def actual_unit_cost(self) -> Money | None:
        return self._actual_unit_cost

    @property
    def purchased_at(self) -> datetime | None:
        return self._purchased_at

    @property
    def line_total(self) -> Decimal:
        return self._unit_price.amount * self._quantity.value

    @property
    def line_deposit(self) -> Decimal:
        return self._unit_deposit.amount * self._quantity.value

    @property
    def is_fully_purchased(self) -> bool:
        return self._purchased_quantity >= self._quantity.value

    def record_purchase(
        self, purchased_quantity: int, actual_unit_cost: Money | None
    ) -> None:
        """Record buying progress (admin enters it from the shopper's bill).

        :raises DomainError: if quantity is outside ``[0, ordered quantity]``.
        """
        if (
            not isinstance(purchased_quantity, int)
            or isinstance(purchased_quantity, bool)
            or purchased_quantity < 0
            or purchased_quantity > self._quantity.value
        ):
            raise DomainError(
                f"Purchased quantity must be between 0 and {self._quantity.value}."
            )
        self._purchased_quantity = purchased_quantity
        self._actual_unit_cost = actual_unit_cost
        self._purchased_at = datetime.now(UTC) if purchased_quantity > 0 else None


class PaymentReceipt(Entity[PaymentReceiptId]):
    """A single money movement on an order (phiếu thu / phiếu hoàn):
    deposit, extra payment, final settlement — or a refund back to the
    customer. Amount is always positive; ``kind`` gives the direction."""

    def __init__(
        self,
        *,
        id_: PaymentReceiptId,
        amount: Money,
        method: ReceiptMethod = ReceiptMethod.CASH,
        kind: ReceiptKind = ReceiptKind.COLLECTION,
        received_at: datetime | None = None,
        note: str = "",
    ) -> None:
        super().__init__(id_=id_)
        self._amount = amount
        self._method = method
        self._kind = kind
        self._received_at = (
            received_at if received_at is not None else datetime.now(UTC)
        )
        self._note = note

    @classmethod
    def create(
        cls,
        *,
        amount: Money,
        method: ReceiptMethod = ReceiptMethod.CASH,
        kind: ReceiptKind = ReceiptKind.COLLECTION,
        received_at: datetime | None = None,
        note: str = "",
    ) -> Self:
        return cls(
            id_=PaymentReceiptId.generate(),
            amount=amount,
            method=method,
            kind=kind,
            received_at=received_at,
            note=note,
        )

    @property
    def amount(self) -> Money:
        return self._amount

    @property
    def method(self) -> ReceiptMethod:
        return self._method

    @property
    def kind(self) -> ReceiptKind:
        return self._kind

    @property
    def received_at(self) -> datetime:
        return self._received_at

    @property
    def note(self) -> str:
        return self._note


class Order(Entity[OrderId]):
    """A customer's pre-order — the aggregate root.

    Owns its lines and payment receipts: money invariants (totals, collected,
    remaining) live here, and children are only reachable through the order.
    ``tracking_code`` is the customer-facing mã Code, immutable after creation.
    ``trip_id`` links the order to at most one buying trip; ``is_separate``
    ("giao riêng") excludes it from consolidation.
    """

    def __init__(
        self,
        *,
        id_: OrderId,
        organization_id: OrganizationId,
        customer_id: CustomerId,
        tracking_code: TrackingCode,
        lines: list[OrderLine],
        receipts: list[PaymentReceipt] | None = None,
        status: OrderStatus = OrderStatus.PENDING,
        is_separate: bool = False,
        trip_id: TripId | None = None,
        note: str = "",
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        if not lines:
            raise DomainError("An order must have at least one line.")
        now = datetime.now(UTC)
        self._organization_id = organization_id
        self._customer_id = customer_id
        self._tracking_code = tracking_code
        self._lines = lines
        self._receipts = receipts if receipts is not None else []
        self._status = status
        self._is_separate = is_separate
        self._trip_id = trip_id
        self._note = note
        self._created_at = created_at if created_at is not None else now
        self._updated_at = updated_at if updated_at is not None else now

    @classmethod
    def create(
        cls,
        *,
        organization_id: OrganizationId,
        customer_id: CustomerId,
        tracking_code: TrackingCode,
        lines: list[OrderLine],
        is_separate: bool = False,
        note: str = "",
    ) -> Self:
        """Factory: create a new PENDING order with a generated id."""
        return cls(
            id_=OrderId.generate(),
            organization_id=organization_id,
            customer_id=customer_id,
            tracking_code=tracking_code,
            lines=lines,
            is_separate=is_separate,
            note=note,
        )

    @property
    def organization_id(self) -> OrganizationId:
        return self._organization_id

    @property
    def customer_id(self) -> CustomerId:
        return self._customer_id

    @property
    def tracking_code(self) -> TrackingCode:
        return self._tracking_code

    @property
    def lines(self) -> list[OrderLine]:
        return list(self._lines)

    @property
    def receipts(self) -> list[PaymentReceipt]:
        return list(self._receipts)

    @property
    def status(self) -> OrderStatus:
        return self._status

    @property
    def is_separate(self) -> bool:
        return self._is_separate

    @property
    def trip_id(self) -> TripId | None:
        return self._trip_id

    @property
    def note(self) -> str:
        return self._note

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    # --- derived money figures ---

    @property
    def total_amount(self) -> Decimal:
        return sum((line.line_total for line in self._lines), Decimal("0"))

    @property
    def deposit_due(self) -> Decimal:
        return sum((line.line_deposit for line in self._lines), Decimal("0"))

    @property
    def total_collected(self) -> Decimal:
        """Net money held: collections minus refunds."""
        return sum(
            (
                r.amount.amount
                if r.kind is ReceiptKind.COLLECTION
                else -r.amount.amount
                for r in self._receipts
            ),
            Decimal("0"),
        )

    @property
    def total_refunded(self) -> Decimal:
        return sum(
            (
                r.amount.amount
                for r in self._receipts
                if r.kind is ReceiptKind.REFUND
            ),
            Decimal("0"),
        )

    @property
    def remaining(self) -> Decimal:
        return self.total_amount - self.total_collected

    @property
    def all_lines_purchased(self) -> bool:
        return all(line.is_fully_purchased for line in self._lines)

    # --- behaviour ---

    def change_status(self, new_status: OrderStatus) -> None:
        """Advance the lifecycle. No-op if unchanged.

        :raises DomainError: if the transition is not allowed, or when
            cancelling an order still attached to a trip.
        """
        if new_status is self._status:
            return
        if new_status not in ALLOWED_ORDER_TRANSITIONS[self._status]:
            raise DomainError(
                f"Cannot change order status from {self._status.value!r} "
                f"to {new_status.value!r}."
            )
        if new_status is OrderStatus.CANCELLED and self._trip_id is not None:
            raise DomainError(
                "Cannot cancel an order attached to a trip; detach it first."
            )
        self._status = new_status
        self._touch()

    def replace_lines(self, lines: list[OrderLine]) -> None:
        """Swap all lines (typo correction). Only while PENDING.

        :raises DomainError: if the order left PENDING or *lines* is empty.
        """
        if self._status is not OrderStatus.PENDING:
            raise DomainError("Order lines can only be edited while pending.")
        if not lines:
            raise DomainError("An order must have at least one line.")
        self._lines = lines
        self._touch()

    def add_receipt(self, receipt: PaymentReceipt) -> None:
        """Record a money movement.

        Collections are rejected on cancelled orders; refunds are allowed
        there (hoàn cọc khi hủy) but can never exceed what was collected.

        :raises DomainError: on a non-positive amount, a collection on a
            cancelled order, or a refund exceeding the collected balance.
        """
        if receipt.amount.amount <= 0:
            raise DomainError("Receipt amount must be positive.")
        if receipt.kind is ReceiptKind.COLLECTION:
            if self._status is OrderStatus.CANCELLED:
                raise DomainError("Cannot collect money on a cancelled order.")
        else:
            if receipt.amount.amount > self.total_collected:
                raise DomainError(
                    "Refund cannot exceed the collected balance "
                    f"({self.total_collected})."
                )
        self._receipts.append(receipt)
        self._touch()

    def remove_receipt(self, receipt_id: PaymentReceiptId) -> bool:
        """Delete a receipt (correction path). Returns False if absent."""
        for receipt in self._receipts:
            if receipt.id_ == receipt_id:
                self._receipts.remove(receipt)
                self._touch()
                return True
        return False

    def find_line(self, line_id: OrderLineId) -> OrderLine | None:
        for line in self._lines:
            if line.id_ == line_id:
                return line
        return None

    def record_line_purchase(
        self,
        line_id: OrderLineId,
        purchased_quantity: int,
        actual_unit_cost: Money | None,
    ) -> OrderLine:
        """Record buying progress on one line; auto-advances to PURCHASED
        when every line is fully bought.

        :raises DomainError: if the line is missing or the order is not
            being purchased.
        """
        if self._status is not OrderStatus.PURCHASING:
            raise DomainError(
                "Purchases can only be recorded while the order is purchasing."
            )
        line = self.find_line(line_id)
        if line is None:
            raise DomainError(f"Order line {line_id.value!r} not found.")
        line.record_purchase(purchased_quantity, actual_unit_cost)
        if self.all_lines_purchased:
            self.change_status(OrderStatus.PURCHASED)
        self._touch()
        return line

    def attach_to_trip(self, trip_id: TripId) -> None:
        """Join a buying trip (gom đơn).

        :raises DomainError: if marked "giao riêng", already in a trip, or not
            in an attachable status.
        """
        if self._is_separate:
            raise DomainError(
                "Order is marked for separate delivery (giao riêng) "
                "and cannot join a trip."
            )
        if self._trip_id is not None:
            raise DomainError("Order already belongs to a trip.")
        if self._status not in (OrderStatus.PENDING, OrderStatus.CONFIRMED):
            raise DomainError(
                f"Only pending/confirmed orders can join a trip "
                f"(current: {self._status.value!r})."
            )
        self._trip_id = trip_id
        self._touch()

    def detach_from_trip(self) -> None:
        """Leave the trip (only while it is still being planned)."""
        if self._trip_id is None:
            return
        self._trip_id = None
        self._touch()

    def set_separate(self, is_separate: bool) -> None:
        """Toggle "giao riêng". Only while not attached to a trip.

        :raises DomainError: if the order belongs to a trip.
        """
        if is_separate == self._is_separate:
            return
        if self._trip_id is not None:
            raise DomainError("Cannot change delivery mode while in a trip.")
        self._is_separate = is_separate
        self._touch()

    def change_note(self, new_note: str) -> None:
        """Replace the free-text note. No-op if unchanged."""
        if new_note == self._note:
            return
        self._note = new_note
        self._touch()

    def _touch(self) -> None:
        """Refresh updated_at to reflect a mutation."""
        self._updated_at = datetime.now(UTC)
