import re
import uuid
from dataclasses import dataclass
from typing import ClassVar, Final, Self

from src.shared.domain.base import DomainError, ValueObject


@dataclass(frozen=True, slots=True, repr=True)
class ProductId(ValueObject):
    """Identity of a Product aggregate.

    :raises DomainError: if value is not a UUID, or when parsing an invalid
        string via :meth:`from_string`.
    """

    value: uuid.UUID

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if not isinstance(self.value, uuid.UUID):
            raise DomainError("Product id must be a UUID.")

    @classmethod
    def generate(cls) -> Self:
        return cls(value=uuid.uuid4())

    @classmethod
    def from_string(cls, raw: str) -> Self:
        """:raises DomainError:"""
        try:
            parsed = uuid.UUID(raw)
        except (ValueError, TypeError, AttributeError) as exc:
            raise DomainError(f"Invalid product id: {raw!r}.") from exc
        return cls(value=parsed)


@dataclass(frozen=True, slots=True, repr=True)
class ProductCode(ValueObject):
    """Tenant-unique product code.

    Not called "SKU": that term means *Stock*-Keeping Unit, an inventory
    concept, whereas this system manages pre-order demand. The product itself
    carries no price — pricing is per sale round (see CampaignProduct).

    :raises DomainError: if the length is outside ``[MIN_LEN, MAX_LEN]`` or the
        value contains characters other than letters, digits, ``-`` or ``_``.
    """

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 64
    _PATTERN: ClassVar[Final[re.Pattern[str]]] = re.compile(r"^[A-Za-z0-9_-]+$")

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        normalized = self.value.strip()
        if len(normalized) < self.MIN_LEN or len(normalized) > self.MAX_LEN:
            raise DomainError(
                f"Product code must be between {self.MIN_LEN} and {self.MAX_LEN} characters.",
            )
        if not self._PATTERN.match(normalized):
            raise DomainError(f"Invalid product code: {self.value!r}.")
        object.__setattr__(self, "value", normalized)


@dataclass(frozen=True, slots=True, repr=True)
class ProductName(ValueObject):
    """Display name of a product.

    :raises DomainError: if the length is outside ``[MIN_LEN, MAX_LEN]``.
    """

    MIN_LEN: ClassVar[Final[int]] = 1
    MAX_LEN: ClassVar[Final[int]] = 255

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if len(self.value) < self.MIN_LEN or len(self.value) > self.MAX_LEN:
            raise DomainError(
                f"Product name must be between {self.MIN_LEN} and {self.MAX_LEN} characters.",
            )


@dataclass(frozen=True, slots=True, repr=True)
class Description(ValueObject):
    """Free-text product description (may be empty).

    :raises DomainError: if longer than ``MAX_LEN``.
    """

    MAX_LEN: ClassVar[Final[int]] = 1000

    value: str

    def __post_init__(self) -> None:
        """:raises DomainError:"""
        if len(self.value) > self.MAX_LEN:
            raise DomainError(
                f"Description must be at most {self.MAX_LEN} characters.",
            )
