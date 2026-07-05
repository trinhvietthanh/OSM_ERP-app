from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.trip.application.dto.trip import CreateTripInput, TripRead
from src.modules.trip.application.exceptions import TripCodeAlreadyExistsError
from src.modules.trip.domain.entities.trip import Trip
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripCode, TripName


class CreateTrip:
    """Create a new trip in the caller's tenant, enforcing code uniqueness."""

    def __init__(self, repo: AbstractTripRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, inp: CreateTripInput
    ) -> TripRead:
        code = TripCode(value=inp.code)
        if await self._repo.get_by_code(organization_id, code) is not None:
            raise TripCodeAlreadyExistsError(inp.code)
        trip = await self._repo.add(
            Trip.create(
                organization_id=organization_id,
                code=code,
                name=TripName(value=inp.name),
                shopper_name=inp.shopper_name,
                departure_date=inp.departure_date,
                arrival_date=inp.arrival_date,
                note=inp.note,
            )
        )
        return TripRead.from_entity(trip)
