import abc
from typing import Any

from src.modules.authenticate.domain.entities.user import User


class AbstractPasswordHasher(abc.ABC):
    """Port for hashing and verifying plaintext passwords."""

    @abc.abstractmethod
    def hash(self, plaintext: str) -> str:
        """Return an opaque hash of *plaintext*."""
        ...

    @abc.abstractmethod
    def verify(self, plaintext: str, hashed: str) -> bool:
        """Return ``True`` if *plaintext* matches *hashed*."""
        ...


class AbstractTokenService(abc.ABC):
    """Port for issuing and decoding JWT access tokens."""

    @property
    @abc.abstractmethod
    def access_ttl_seconds(self) -> int:
        """Lifetime of an access token, in seconds."""
        ...

    @abc.abstractmethod
    def create_access_token(self, user: User) -> str:
        """Issue a signed access token for *user*."""
        ...

    @abc.abstractmethod
    def decode(self, token: str) -> dict[str, Any]:
        """Decode and verify *token*; raise on invalid/expired tokens."""
        ...
