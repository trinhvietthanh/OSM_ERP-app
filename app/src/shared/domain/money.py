from dataclasses import dataclass
from decimal import Decimal

from src.shared.domain.base import DomainError, ValueObject


@dataclass(frozen=True, slots=True, repr=True)
class Money(ValueObject):
    """Non-negative monetary amount. Currency is an org-level concern.

    Shared across modules: campaign prices/deposits, order line prices,
    payment receipt amounts.

    :raises DomainError: if amount is not a :class:`~decimal.Decimal` or is negative.
    """

    amount: Decimal

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.amount, Decimal):
            raise DomainError("Money amount must be a Decimal.")
        if self.amount < 0:
            raise DomainError("Money amount cannot be negative.")
