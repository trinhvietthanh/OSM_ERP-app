import uuid
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Final, Self

from src.shared.domain.base import DomainError, ValueObject


@dataclass(frozen=True, slots=True, repr=True)
class OrganizationId(ValueObject):
    """Identity of an Organization aggregate.

    :raises DomainError: if value is not a UUID, or when parsing an invalid
        string via :meth:`from_string`.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, uuid.UUID):
            raise DomainError("Organization id must be a UUID.")

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        try:
            parsed = uuid.UUID(raw)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DomainError(f"Invalid organization id: {raw!r}.") from exc
        return cls(value=parsed)


class OrganizationStatus(Enum):
    ACTIVE = "active"
    SUSPENDED = "suspended"


@dataclass(frozen=True, slots=True, repr=True)
class OrganizationName(ValueObject):
    """raises DomainError"""

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 255

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        self._validate_title_length(self.value)

    def _validate_title_length(self, title_value: str) -> None:
        """:raises DomainError:"""
        if len(title_value) < self.MIN_LEN or len(title_value) > self.MAX_LEN:
            raise DomainError(
                f"Title must be between {self.MIN_LEN} and {self.MAX_LEN} characters.",
            )


