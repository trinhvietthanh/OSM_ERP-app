from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.trip.application.dto.trip import TripRead, UpdateTripInput
from src.modules.trip.application.exceptions import TripNotFoundError
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripId, TripName


class UpdateTrip:
    """Apply a partial update (name/shopper/dates/note) to an existing trip."""

    def __init__(self, repo: AbstractTripRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, id_: TripId, inp: UpdateTripInput
    ) -> TripRead:
        trip = await self._repo.get(organization_id, id_)
        if trip is None:
            raise TripNotFoundError(id_.value)

        if inp.name is not None:
            trip.rename(TripName(value=inp.name))
        if inp.shopper_name is not None:
            trip.change_shopper_name(inp.shopper_name)
        if inp.departure_date is not None:
            trip.set_departure_date(inp.departure_date)
        if inp.arrival_date is not None:
            trip.set_arrival_date(inp.arrival_date)
        if inp.note is not None:
            trip.change_note(inp.note)

        saved = await self._repo.save(trip)
        if saved is None:
            raise TripNotFoundError(id_.value)
        return TripRead.from_entity(saved)
