from typing import Any

from src.shared.domain.base import DomainError


class OrderNotFoundError(DomainError):
    """Raised when a command targets an order that does not exist (in the
    caller's tenant)."""

    def __init__(self, id_: Any) -> None:
        super().__init__(f"Order {id_!r} not found.")


class ReceiptNotFoundError(DomainError):
    """Raised when a command targets a receipt that does not exist on the
    order."""

    def __init__(self, id_: Any) -> None:
        super().__init__(f"Receipt {id_!r} not found.")


class OrderLineNotFoundError(DomainError):
    """Raised when a command targets a line that does not exist on the order."""

    def __init__(self, id_: Any) -> None:
        super().__init__(f"Order line {id_!r} not found.")


class TrackingCodeGenerationError(DomainError):
    """Raised when a unique tracking code could not be generated (practically
    unreachable with the 31^8 keyspace)."""

    def __init__(self) -> None:
        super().__init__("Could not generate a unique tracking code; try again.")
