from typing import Any

from src.shared.domain.base import DomainError


class OrganizationNotFoundError(DomainError):
    """Raised when a command targets an organization id that does not exist."""

    def __init__(self, id_: Any) -> None:
        super().__init__(f"Organization {id_!r} not found.")


class OrganizationAlreadyExistsError(DomainError):
    """Raised when creating an organization with an already-used name."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Organization with name {name!r} already exists.")
