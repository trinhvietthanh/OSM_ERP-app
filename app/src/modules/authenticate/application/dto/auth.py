from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from src.modules.authenticate.domain.entities.user import User


class LoginInput(BaseModel):
    """Payload for the Login command."""

    email: str
    password: str


class UserRead(BaseModel):
    """Read model returned by auth queries (e.g. ``GET /auth/me``)."""

    id: UUID
    organization_id: UUID
    email: str
    username: str
    role: str
    is_active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, user: User) -> Self:
        return cls(
            id=user.id_.value,
            organization_id=user.organization_id.value,
            email=user.email.value,
            username=user.username.value,
            role=user.role.value,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
        )


class TokenRead(BaseModel):
    """Token response for a successful login."""

    access_token: str
    token_type: str = "bearer"
    expires_in: int
