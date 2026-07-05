import secrets
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Final, Self

from src.shared.domain.base import DomainError, ValueObject


@dataclass(frozen=True, slots=True, repr=True)
class OrderId(ValueObject):
    """Identity of an Order aggregate.

    :raises DomainError: if value is not a UUID, or when parsing an invalid
        string via :meth:`from_string`.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, uuid.UUID):
            raise DomainError("Order id must be a UUID.")

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        try:
            parsed = uuid.UUID(raw)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DomainError(f"Invalid order id: {raw!r}.") from exc
        return cls(value=parsed)


@dataclass(frozen=True, slots=True, repr=True)
class OrderLineId(ValueObject):
    """Identity of an order line (child of the Order aggregate).

    :raises DomainError: if value is not a UUID, or when parsing an invalid
        string via :meth:`from_string`.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, uuid.UUID):
            raise DomainError("Order line id must be a UUID.")

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        try:
            parsed = uuid.UUID(raw)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DomainError(f"Invalid order line id: {raw!r}.") from exc
        return cls(value=parsed)


@dataclass(frozen=True, slots=True, repr=True)
class PaymentReceiptId(ValueObject):
    """Identity of a payment receipt (child of the Order aggregate).

    :raises DomainError: if value is not a UUID, or when parsing an invalid
        string via :meth:`from_string`.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, uuid.UUID):
            raise DomainError("Payment receipt id must be a UUID.")

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        try:
            parsed = uuid.UUID(raw)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DomainError(f"Invalid payment receipt id: {raw!r}.") from exc
        return cls(value=parsed)


@dataclass(frozen=True, slots=True, repr=True)
class TrackingCode(ValueObject):
    """Customer-facing order tracking code (mã Code).

    8 characters from an unambiguous alphabet (no ``0/O``, ``1/I/L``), globally
    unique so the future public lookup page can resolve it without a tenant
    context. Generated with a CSPRNG — the 31^8 (~8.5e11) keyspace makes codes
    unguessable in practice.

    :raises DomainError: if not exactly ``LENGTH`` chars from ``ALPHABET``.
    """

    LENGTH: ClassVar[Final[int]] = 8
    ALPHABET: ClassVar[Final[str]] = "ABCDEFGHJKMNPQRSTUVWXYZ23456789"

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        normalized = self.value.strip().upper()
        if len(normalized) != self.LENGTH or any(
            c not in self.ALPHABET for c in normalized
        ):
            raise DomainError(f"Invalid tracking code: {self.value!r}.")
        object.__setattr__(self, "value", normalized)

    @classmethod
    def generate(cls) -> Self:
        return cls(
            value="".join(secrets.choice(cls.ALPHABET) for _ in range(cls.LENGTH))
        )

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        return cls(value=raw)


@dataclass(frozen=True, slots=True, repr=True)
class Quantity(ValueObject):
    """Ordered quantity of a line item (>= 1).

    :raises DomainError: if not a positive int.
    """

    value: int

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, int) or isinstance(self.value, bool):
            raise DomainError("Quantity must be an integer.")
        if self.value < 1:
            raise DomainError("Quantity must be at least 1.")


class OrderStatus(Enum):
    """Lifecycle of a customer order (đơn hàng)."""

    PENDING = "pending"  # Chờ xử lý
    CONFIRMED = "confirmed"  # Đã chốt (đã cọc)
    PURCHASING = "purchasing"  # Đang mua
    PURCHASED = "purchased"  # Đã mua
    ARRIVED = "arrived"  # Đã về VN
    DELIVERED = "delivered"  # Đã giao (terminal)
    CANCELLED = "cancelled"  # Đã hủy (terminal)


#: Allowed forward transitions. Cancellation is only possible before goods
#: are purchased (hàng xách tay hầu như không trả lại được).
ALLOWED_ORDER_TRANSITIONS: Final[dict[OrderStatus, frozenset[OrderStatus]]] = {
    OrderStatus.PENDING: frozenset({OrderStatus.CONFIRMED, OrderStatus.CANCELLED}),
    OrderStatus.CONFIRMED: frozenset({OrderStatus.PURCHASING, OrderStatus.CANCELLED}),
    OrderStatus.PURCHASING: frozenset({OrderStatus.PURCHASED, OrderStatus.CANCELLED}),
    OrderStatus.PURCHASED: frozenset({OrderStatus.ARRIVED}),
    OrderStatus.ARRIVED: frozenset({OrderStatus.DELIVERED}),
    OrderStatus.DELIVERED: frozenset(),
    OrderStatus.CANCELLED: frozenset(),
}


class ReceiptMethod(Enum):
    """How a payment was collected."""

    CASH = "cash"
    BANK_TRANSFER = "bank_transfer"
    OTHER = "other"


class ReceiptKind(Enum):
    """Direction of a receipt: money in (collection) or money back (refund)."""

    COLLECTION = "collection"
    REFUND = "refund"
