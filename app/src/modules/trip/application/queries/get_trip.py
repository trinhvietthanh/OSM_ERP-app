from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.trip.application.dto.trip import TripRead
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripId


class GetTrip:
    """Fetch a single trip in the caller's tenant."""

    def __init__(self, repo: AbstractTripRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, id_: TripId
    ) -> TripRead | None:
        trip = await self._repo.get(organization_id, id_)
        return TripRead.from_entity(trip) if trip is not None else None
