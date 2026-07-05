from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.session import get_session
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.infrastructure.repository import (
    SqlAlchemyProductRepository,
)


def get_product_repository(
    session: AsyncSession = Depends(get_session),
) -> AbstractProductRepository:
    return SqlAlchemyProductRepository(session)
