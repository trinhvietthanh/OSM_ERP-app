import re
import uuid
from dataclasses import dataclass
from typing import ClassVar, Final, Self

from src.shared.domain.base import DomainError, ValueObject


@dataclass(frozen=True, slots=True, repr=True)
class CustomerId(ValueObject):
    """Identity of a Customer aggregate.

    :raises DomainError: if value is not a UUID, or when parsing an invalid
        string via :meth:`from_string`.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, uuid.UUID):
            raise DomainError("Customer id must be a UUID.")

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        try:
            parsed = uuid.UUID(raw)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DomainError(f"Invalid customer id: {raw!r}.") from exc
        return cls(value=parsed)


@dataclass(frozen=True, slots=True, repr=True)
class CustomerName(ValueObject):
    """Display name of a customer.

    :raises DomainError: if the length is outside ``[MIN_LEN, MAX_LEN]``.
    """

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 255

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        normalized = self.value.strip()
        if len(normalized) < self.MIN_LEN or len(normalized) > self.MAX_LEN:
            raise DomainError(
                f"Customer name must be between {self.MIN_LEN} and {self.MAX_LEN} characters.",
            )
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True, repr=True)
class PhoneNumber(ValueObject):
    """Customer phone number. Digits with optional ``+``, spaces, ``-``, ``.``.

    Not unique — several customers may share a household phone, or come from
    channels (Facebook/Zalo) where the phone is a soft identifier.

    :raises DomainError: if the length is outside ``[MIN_LEN, MAX_LEN]`` or the
        value contains other characters.
    """

    MIN_LEN: ClassVar[Final[int]] = 6
    MAX_LEN: ClassVar[Final[int]] = 20
    _PATTERN: ClassVar[Final[re.Pattern[str]]] = re.compile(r"^\+?[0-9 .\-]+$")

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        normalized = self.value.strip()
        if len(normalized) < self.MIN_LEN or len(normalized) > self.MAX_LEN:
            raise DomainError(
                f"Phone number must be between {self.MIN_LEN} and {self.MAX_LEN} characters.",
            )
        if not self._PATTERN.match(normalized):
            raise DomainError(f"Invalid phone number: {self.value!r}.")
        object.__setattr__(self, "value", normalized)
