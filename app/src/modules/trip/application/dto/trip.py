from datetime import date, datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from src.modules.trip.domain.entities.trip import Trip


class CreateTripInput(BaseModel):
    """Payload for the CreateTrip command."""

    code: str
    name: str
    shopper_name: str = ""
    departure_date: date | None = None
    arrival_date: date | None = None
    note: str = ""


class UpdateTripInput(BaseModel):
    """Partial payload for the UpdateTrip command. Status has its own command.

    ``shopper_name=""`` / ``note=""`` clear the field; ``None`` leaves unchanged.
    """

    name: str | None = None
    shopper_name: str | None = None
    departure_date: date | None = None
    arrival_date: date | None = None
    note: str | None = None


class ChangeTripStatusInput(BaseModel):
    """Payload for the ChangeTripStatus command."""

    status: str  # planning | buying | shipping | arrived | completed | cancelled


class AttachOrdersInput(BaseModel):
    """Payload for attaching orders to a trip (gom đơn)."""

    order_ids: list[UUID]


class TripRead(BaseModel):
    """Read model returned by trip commands and queries."""

    id: UUID
    organization_id: UUID
    code: str
    name: str
    status: str
    shopper_name: str
    departure_date: date | None = None
    arrival_date: date | None = None
    note: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, trip: Trip) -> Self:
        return cls(
            id=trip.id_.value,
            organization_id=trip.organization_id.value,
            code=trip.code.value,
            name=trip.name.value,
            status=trip.status.value,
            shopper_name=trip.shopper_name,
            departure_date=trip.departure_date,
            arrival_date=trip.arrival_date,
            note=trip.note,
            created_at=trip.created_at,
            updated_at=trip.updated_at,
        )
