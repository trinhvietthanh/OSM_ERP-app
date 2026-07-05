from datetime import UTC, datetime

from src.modules.authenticate.domain.value_objects.user import (
    Email,
    PasswordHash,
    UserId,
    UserRole,
    Username,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.shared.domain.base import Entity


class User(Entity[UserId]):
    """Aggregate root representing an authenticated user within a tenant.

    The user belongs to exactly one organization (the ERP tenant). This
    aggregate is read-mostly from the auth module's perspective (login / me);
    users are seeded rather than self-registered, so it exposes no mutating
    domain operations beyond construction.
    """

    def __init__(
        self,
        *,
        id_: UserId,
        organization_id: OrganizationId,
        email: Email,
        username: Username,
        password_hash: PasswordHash,
        role: UserRole = UserRole.MEMBER,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        now = datetime.now(UTC)
        self._organization_id = organization_id
        self._email = email
        self._username = username
        self._password_hash = password_hash
        self._role = role
        self._is_active = is_active
        self._created_at = created_at if created_at is not None else now
        self._updated_at = updated_at if updated_at is not None else now

    @property
    def organization_id(self) -> OrganizationId:
        return self._organization_id

    @property
    def email(self) -> Email:
        return self._email

    @property
    def username(self) -> Username:
        return self._username

    @property
    def password_hash(self) -> PasswordHash:
        return self._password_hash

    @property
    def role(self) -> UserRole:
        return self._role

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at
