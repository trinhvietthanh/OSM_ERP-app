from typing import Any

from src.shared.domain.base import DomainError


class SaleRoundNotFoundError(DomainError):
    """Raised when a command targets a sale round that does not exist (in the
    caller's tenant)."""

    def __init__(self, id_: Any) -> None:
        super().__init__(f"Sale round {id_!r} not found.")


class SaleRoundCodeAlreadyExistsError(DomainError):
    """Raised when creating a round with a code already used in the tenant."""

    def __init__(self, code: str) -> None:
        super().__init__(f"Sale round with code {code!r} already exists.")


class CampaignProductNotFoundError(DomainError):
    """Raised when a command targets a campaign product that does not exist (in
    the caller's tenant)."""

    def __init__(self, id_: Any) -> None:
        super().__init__(f"Campaign product {id_!r} not found.")


class CampaignProductAlreadyExistsError(DomainError):
    """Raised when a product is already offered in the target sale round."""

    def __init__(self) -> None:
        super().__init__("Product is already offered in this sale round.")
