import re
import uuid
from dataclasses import dataclass, field
from enum import Enum
from typing import ClassVar, Final, Self

from src.shared.domain.base import DomainError, ValueObject


@dataclass(frozen=True, slots=True, repr=True)
class UserId(ValueObject):
    """Identity of a User aggregate.

    :raises DomainError: if value is not a UUID, or when parsing an invalid
        string via :meth:`from_string`.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, uuid.UUID):
            raise DomainError("User id must be a UUID.")

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        try:
            parsed = uuid.UUID(raw)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DomainError(f"Invalid user id: {raw!r}.") from exc
        return cls(value=parsed)


class UserRole(Enum):
    ADMIN = "admin"
    MEMBER = "member"


@dataclass(frozen=True, slots=True, repr=True)
class Email(ValueObject):
    """Lowercased, RFC-ish email address.

    The value is normalized to lowercase on construction so equality and
    uniqueness lookups are case-insensitive without needing a ``CITEXT``
    extension.

    :raises DomainError: if the value is not a plausible email.
    """

    MIN_LEN: ClassVar[Final[int]] = 3
    MAX_LEN: ClassVar[Final[int]] = 254
    _PATTERN: ClassVar[Final[re.Pattern[str]]] = re.compile(
        r"^[^@\s]+@[^@\s]+\.[^@\s]+$"
    )

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        normalized = self.value.strip().lower()
        if len(normalized) < self.MIN_LEN or len(normalized) > self.MAX_LEN:
            raise DomainError("Email length is invalid.")
        if not self._PATTERN.match(normalized):
            raise DomainError(f"Invalid email: {self.value!r}.")
        object.__setattr__(self, "value", normalized)

    @classmethod
    def from_string(cls, raw: str) -> Self:
        return cls(value=raw)


@dataclass(frozen=True, slots=True, repr=True)
class Username(ValueObject):
    """Display name of a user.

    :raises DomainError: if the length is outside ``[MIN_LEN, MAX_LEN]``.
    """

    MIN_LEN: ClassVar[Final[int]] = 3
    MAX_LEN: ClassVar[Final[int]] = 64

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if len(self.value) < self.MIN_LEN or len(self.value) > self.MAX_LEN:
            raise DomainError(
                f"Username must be between {self.MIN_LEN} and {self.MAX_LEN} characters.",
            )


@dataclass(frozen=True, slots=True, repr=False)
class PasswordHash(ValueObject):
    """Opaque password hash (e.g. bcrypt). Hidden from ``repr`` to avoid leaking.

    :raises DomainError: if the value is not a non-empty string.
    """

    value: str = field(repr=False)

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, str) or not self.value:
            raise DomainError("Password hash must be a non-empty string.")
