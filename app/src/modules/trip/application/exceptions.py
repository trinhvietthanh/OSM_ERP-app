from typing import Any

from src.shared.domain.base import DomainError


class TripNotFoundError(DomainError):
    """Raised when a command targets a trip that does not exist (in the
    caller's tenant)."""

    def __init__(self, id_: Any) -> None:
        super().__init__(f"Trip {id_!r} not found.")


class TripCodeAlreadyExistsError(DomainError):
    """Raised when creating a trip with a code already used in the tenant."""

    def __init__(self, code: str) -> None:
        super().__init__(f"Trip with code {code!r} already exists.")


class OrderNotAttachableError(DomainError):
    """Raised when an order cannot be attached to / detached from a trip
    (wrong status, marked "giao riêng", or already in another trip)."""

    def __init__(self, reason: str) -> None:
        super().__init__(reason)
