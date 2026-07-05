from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.trip.domain.entities.trip import Trip
from src.modules.trip.domain.value_objects.trip import TripCode, TripId, TripName
from src.modules.trip.infrastructure.models import TripModel


def trip_model_to_entity(model: TripModel) -> Trip:
    return Trip(
        id_=TripId(value=model.id),
        organization_id=OrganizationId(value=model.organization_id),
        code=TripCode(value=model.code),
        name=TripName(value=model.name),
        status=model.status,
        shopper_name=model.shopper_name,
        departure_date=model.departure_date,
        arrival_date=model.arrival_date,
        note=model.note,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def trip_entity_to_model(entity: Trip) -> TripModel:
    return TripModel(
        id=entity.id_.value,
        organization_id=entity.organization_id.value,
        code=entity.code.value,
        name=entity.name.value,
        status=entity.status,
        shopper_name=entity.shopper_name,
        departure_date=entity.departure_date,
        arrival_date=entity.arrival_date,
        note=entity.note,
    )


def apply_trip_to_model(entity: Trip, model: TripModel) -> None:
    """Copy mutable fields. ``id``/``organization_id``/``code`` are immutable."""
    model.name = entity.name.value
    model.status = entity.status
    model.shopper_name = entity.shopper_name
    model.departure_date = entity.departure_date
    model.arrival_date = entity.arrival_date
    model.note = entity.note
