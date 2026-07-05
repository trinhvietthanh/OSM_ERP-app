import bcrypt

from src.modules.authenticate.domain.services import AbstractPasswordHasher


class BcryptPasswordHasher(AbstractPasswordHasher):
    """Password hasher backed by the ``bcrypt`` library."""

    def hash(self, plaintext: str) -> str:
        return bcrypt.hashpw(
            plaintext.encode("utf-8"), bcrypt.gensalt()
        ).decode("utf-8")

    def verify(self, plaintext: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(
                plaintext.encode("utf-8"), hashed.encode("utf-8")
            )
        except (ValueError, TypeError):
            # Malformed hash or wrong algorithm — treat as failed verification.
            return False
