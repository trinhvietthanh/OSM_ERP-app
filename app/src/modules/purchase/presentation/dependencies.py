from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.session import get_session
from src.modules.purchase.domain.repository import AbstractOrderRepository
from src.modules.purchase.infrastructure.repository import SqlAlchemyOrderRepository


def get_order_repository(
    session: AsyncSession = Depends(get_session),
) -> AbstractOrderRepository:
    return SqlAlchemyOrderRepository(session)
