from typing import Any

from src.shared.domain.base import DomainError


class CustomerNotFoundError(DomainError):
    """Raised when a command targets a customer that does not exist (in the
    caller's tenant)."""

    def __init__(self, id_: Any) -> None:
        super().__init__(f"Customer {id_!r} not found.")
