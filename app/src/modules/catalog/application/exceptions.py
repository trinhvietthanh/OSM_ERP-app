from typing import Any

from src.shared.domain.base import DomainError


class ProductNotFoundError(DomainError):
    """Raised when a command targets a product id that does not exist (in the
    caller's tenant)."""

    def __init__(self, id_: Any) -> None:
        super().__init__(f"Product {id_!r} not found.")


class ProductCodeAlreadyExistsError(DomainError):
    """Raised when creating a product with a code already used in the tenant."""

    def __init__(self, code: str) -> None:
        super().__init__(f"Product with code {code!r} already exists.")
