from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.session import get_session
from src.modules.trip.domain.repository import AbstractTripRepository
from src.modules.trip.infrastructure.repository import SqlAlchemyTripRepository


def get_trip_repository(
    session: AsyncSession = Depends(get_session),
) -> AbstractTripRepository:
    return SqlAlchemyTripRepository(session)
