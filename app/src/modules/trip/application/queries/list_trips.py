from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.trip.application.dto.trip import TripRead
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripStatus


class ListTrips:
    """List the tenant's trips, optionally filtered by status."""

    def __init__(self, repo: AbstractTripRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        organization_id: OrganizationId,
        status: TripStatus | None = None,
    ) -> list[TripRead]:
        trips = await self._repo.list(organization_id, status=status)
        return [TripRead.from_entity(t) for t in trips]
