import re
import uuid
from dataclasses import dataclass
from enum import Enum
from typing import ClassVar, Final, Self

from src.shared.domain.base import DomainError, ValueObject


@dataclass(frozen=True, slots=True, repr=True)
class TripId(ValueObject):
    """Identity of a Trip aggregate.

    :raises DomainError: if value is not a UUID, or when parsing an invalid
        string via :meth:`from_string`.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, uuid.UUID):
            raise DomainError("Trip id must be a UUID.")

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        try:
            parsed = uuid.UUID(raw)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DomainError(f"Invalid trip id: {raw!r}.") from exc
        return cls(value=parsed)


@dataclass(frozen=True, slots=True, repr=True)
class TripCode(ValueObject):
    """Tenant-unique trip code (e.g. ``JP-2026-07``).

    :raises DomainError: if the length is outside ``[MIN_LEN, MAX_LEN]`` or the
        value contains characters other than letters, digits, ``-``, ``_``,
        ``.`` or ``/``.
    """

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 64
    _PATTERN: ClassVar[Final[re.Pattern[str]]] = re.compile(r"^[A-Za-z0-9._/-]+$")

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        normalized = self.value.strip()
        if len(normalized) < self.MIN_LEN or len(normalized) > self.MAX_LEN:
            raise DomainError(
                f"Trip code must be between {self.MIN_LEN} and {self.MAX_LEN} characters.",
            )
        if not self._PATTERN.match(normalized):
            raise DomainError(f"Invalid trip code: {self.value!r}.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True, repr=True)
class TripName(ValueObject):
    """Display name of a trip.

    :raises DomainError: if the length is outside ``[MIN_LEN, MAX_LEN]``.
    """

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 255

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if len(self.value) < self.MIN_LEN or len(self.value) > self.MAX_LEN:
            raise DomainError(
                f"Trip name must be between {self.MIN_LEN} and {self.MAX_LEN} characters.",
            )


class TripStatus(Enum):
    """Lifecycle of a buying trip (chuyến hàng)."""

    PLANNING = "planning"
    BUYING = "buying"
    SHIPPING = "shipping"
    ARRIVED = "arrived"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


#: Allowed forward transitions. Anything not listed raises DomainError.
ALLOWED_TRIP_TRANSITIONS: Final[dict[TripStatus, frozenset[TripStatus]]] = {
    TripStatus.PLANNING: frozenset({TripStatus.BUYING, TripStatus.CANCELLED}),
    TripStatus.BUYING: frozenset({TripStatus.SHIPPING, TripStatus.CANCELLED}),
    TripStatus.SHIPPING: frozenset({TripStatus.ARRIVED}),
    TripStatus.ARRIVED: frozenset({TripStatus.COMPLETED}),
    TripStatus.COMPLETED: frozenset(),
    TripStatus.CANCELLED: frozenset(),
}
