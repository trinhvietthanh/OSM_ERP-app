from datetime import UTC, datetime, timedelta
from typing import Any

import jwt

from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.domain.services import AbstractTokenService
from src.modules.authenticate.infrastructure.settings import JwtSettings


class JwtTokenService(AbstractTokenService):
    """JWT access-token service using ``PyJWT`` (HS256) and :class:`JwtSettings`.

    ``decode`` raises ``jwt.ExpiredSignatureError`` / ``jwt.InvalidTokenError``
    on bad tokens; callers (the ``get_current_user`` dependency) translate
    those into HTTP 401.
    """

    def __init__(self, settings: JwtSettings) -> None:
        self._settings = settings

    @property
    def access_ttl_seconds(self) -> int:
        return self._settings.access_expire_minutes * 60

    def create_access_token(self, user: User) -> str:
        now = datetime.now(UTC)
        payload = {
            "sub": str(user.id_.value),
            "tenant": str(user.organization_id.value),
            "role": user.role.value,
            "type": "access",
            "iat": now,
            "exp": now + timedelta(seconds=self.access_ttl_seconds),
        }
        return jwt.encode(
            payload, self._settings.secret, algorithm=self._settings.algorithm
        )

    def decode(self, token: str) -> dict[str, Any]:
        return jwt.decode(
            token,
            self._settings.secret,
            algorithms=[self._settings.algorithm],
        )
