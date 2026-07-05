from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.infrastructure.postgres.session import get_session
from src.modules.campaign.domain.repository import (
    AbstractCampaignProductRepository,
    AbstractSaleRoundRepository,
)
from src.modules.campaign.infrastructure.repository import (
    SqlAlchemyCampaignProductRepository,
    SqlAlchemySaleRoundRepository,
)


def get_sale_round_repository(
    session: AsyncSession = Depends(get_session),
) -> AbstractSaleRoundRepository:
    return SqlAlchemySaleRoundRepository(session)


def get_campaign_product_repository(
    session: AsyncSession = Depends(get_session),
) -> AbstractCampaignProductRepository:
    return SqlAlchemyCampaignProductRepository(session)
