from datetime import UTC, datetime
from typing import Self

from src.modules.organization.domain.value_objects.organization import (
    OrganizationId,
    OrganizationName,
    OrganizationStatus,
)
from src.shared.domain.base import Entity


class Organization(Entity[OrganizationId]):
    """Aggregate root representing an organization (ERP tenant)."""

    def __init__(
        self,
        *,
        id_: OrganizationId,
        name: OrganizationName,
        status: OrganizationStatus = OrganizationStatus.ACTIVE,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        now = datetime.now(UTC)
        self._name = name
        self._status = status
        self._created_at = created_at if created_at is not None else now
        self._updated_at = updated_at if updated_at is not None else now

    @classmethod
    def create(cls, *, name: OrganizationName) -> Self:
        """Factory: create a new active organization with a generated id."""
        return cls(id_=OrganizationId.generate(), name=name)

    @property
    def name(self) -> OrganizationName:
        return self._name

    @property
    def status(self) -> OrganizationStatus:
        return self._status

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def rename(self, new_name: OrganizationName) -> None:
        """Rename the organization. No-op if the name is unchanged."""
        if new_name == self._name:
            return
        self._name = new_name
        self._touch()

    def suspend(self) -> None:
        """Mark the organization as suspended. Idempotent."""
        if self._status is OrganizationStatus.SUSPENDED:
            return
        self._status = OrganizationStatus.SUSPENDED
        self._touch()

    def reactivate(self) -> None:
        """Mark the organization as active. Idempotent."""
        if self._status is OrganizationStatus.ACTIVE:
            return
        self._status = OrganizationStatus.ACTIVE
        self._touch()

    def _touch(self) -> None:
        """Refresh updated_at to reflect a mutation."""
        self._updated_at = datetime.now(UTC)
