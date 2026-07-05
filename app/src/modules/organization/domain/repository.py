import abc
from collections.abc import Sequence

from src.modules.organization.domain.entities.organization import Organization
from src.modules.organization.domain.value_objects.organization import (
    OrganizationId,
    OrganizationName,
)


class AbstractOrganizationRepository(abc.ABC):
    """Port for persisting Organization aggregates.

    Implementations live in the infrastructure layer (e.g.
    :class:`SqlAlchemyOrganizationRepository`). This interface depends only on
    domain types and never on SQLAlchemy.
    """

    @abc.abstractmethod
    async def add(self, organization: Organization) -> Organization:
        """Insert a new organization and return the persisted aggregate."""
        ...

    @abc.abstractmethod
    async def get(self, id_: OrganizationId) -> Organization | None:
        """Return the organization with *id_*, or ``None`` if not found."""
        ...

    @abc.abstractmethod
    async def get_by_name(self, name: OrganizationName) -> Organization | None:
        """Return the organization with *name*, or ``None`` if not found."""
        ...

    @abc.abstractmethod
    async def list(self) -> Sequence[Organization]:
        """Return all organizations."""
        ...

    @abc.abstractmethod
    async def save(self, organization: Organization) -> Organization | None:
        """Persist changes to an existing organization; ``None`` if not found."""
        ...
