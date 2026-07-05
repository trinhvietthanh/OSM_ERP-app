from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.modules.trip.domain.entities.trip import Trip
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.domain.value_objects.trip import TripCode, TripId, TripStatus
from src.modules.trip.infrastructure.mappers import (
    apply_trip_to_model,
    trip_entity_to_model,
    trip_model_to_entity,
)
from src.modules.trip.infrastructure.models import TripModel


class SqlAlchemyTripRepository(AbstractTripRepository):
    """Async SQLAlchemy implementation of the Trip repository.

    Tenant-aware: every read is qualified by ``organization_id``. The
    repository never commits; the caller owns the transaction.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, trip: Trip) -> Trip:
        model = trip_entity_to_model(trip)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["created_at", "updated_at"])
        return trip_model_to_entity(model)

    async def get(self, organization_id: OrganizationId, id_: TripId) -> Trip | None:
        stmt = select(TripModel).where(
            TripModel.id == id_.value,
            TripModel.organization_id == organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return trip_model_to_entity(model) if model is not None else None

    async def get_by_code(
        self, organization_id: OrganizationId, code: TripCode
    ) -> Trip | None:
        stmt = select(TripModel).where(
            TripModel.organization_id == organization_id.value,
            TripModel.code == code.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return trip_model_to_entity(model) if model is not None else None

    async def list(
        self,
        organization_id: OrganizationId,
        status: TripStatus | None = None,
    ) -> Sequence[Trip]:
        stmt = select(TripModel).where(
            TripModel.organization_id == organization_id.value
        )
        if status is not None:
            stmt = stmt.where(TripModel.status == status)
        stmt = stmt.order_by(TripModel.created_at.desc())
        models = (await self._session.scalars(stmt)).all()
        return [trip_model_to_entity(m) for m in models]

    async def save(self, trip: Trip) -> Trip | None:
        stmt = select(TripModel).where(
            TripModel.id == trip.id_.value,
            TripModel.organization_id == trip.organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        if model is None:
            return None
        apply_trip_to_model(trip, model)
        await self._session.flush()
        await self._session.refresh(model)
        return trip_model_to_entity(model)
