import uuid
from dataclasses import dataclass
from typing import Self

from src.shared.domain.base import DomainError, ValueObject
from src.shared.domain.money import Money  # noqa: F401  (re-export; Money moved to shared)


@dataclass(frozen=True, slots=True, repr=True)
class CampaignProductId(ValueObject):
    """Identity of a CampaignProduct aggregate.

    :raises DomainError: if value is not a UUID, or when parsing an invalid
        string via :meth:`from_string`.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, uuid.UUID):
            raise DomainError("Campaign product id must be a UUID.")

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        try:
            parsed = uuid.UUID(raw)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DomainError(f"Invalid campaign product id: {raw!r}.") from exc
        return cls(value=parsed)


