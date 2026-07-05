import abc
from collections.abc import Sequence

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.trip.domain.entities.trip import Trip
from src.modules.trip.domain.value_objects.trip import TripCode, TripId, TripStatus


class AbstractTripRepository(abc.ABC):
    """Port for persisting Trip aggregates, scoped to a tenant."""

    @abc.abstractmethod
    async def add(self, trip: Trip) -> Trip:
        """Insert a new trip and return the persisted aggregate."""
        ...

    @abc.abstractmethod
    async def get(self, organization_id: OrganizationId, id_: TripId) -> Trip | None:
        """Return the tenant's trip with *id_*, or ``None``."""
        ...

    @abc.abstractmethod
    async def get_by_code(
        self, organization_id: OrganizationId, code: TripCode
    ) -> Trip | None:
        """Return the tenant's trip with *code*, or ``None``."""
        ...

    @abc.abstractmethod
    async def list(
        self,
        organization_id: OrganizationId,
        status: TripStatus | None = None,
    ) -> Sequence[Trip]:
        """Return the tenant's trips, newest first, optionally by status."""
        ...

    @abc.abstractmethod
    async def save(self, trip: Trip) -> Trip | None:
        """Persist changes to an existing trip; ``None`` if not found."""
        ...
