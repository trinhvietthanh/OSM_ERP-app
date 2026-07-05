from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.campaign.domain.entities.campaign_product import CampaignProduct
from src.modules.campaign.domain.entities.sale_round import SaleRound
from src.modules.campaign.domain.repository import (
    AbstractCampaignProductRepository,
    AbstractSaleRoundRepository,
)
from src.modules.campaign.domain.value_objects.campaign_product import (
    CampaignProductId,
)
from src.modules.campaign.domain.value_objects.sale_round import (
    RoundCode,
    SaleRoundId,
)
from src.modules.campaign.infrastructure.mappers import (
    apply_campaign_product_to_model,
    apply_sale_round_to_model,
    campaign_product_entity_to_model,
    campaign_product_model_to_entity,
    sale_round_entity_to_model,
    sale_round_model_to_entity,
)
from src.modules.campaign.infrastructure.models import (
    CampaignProductModel,
    SaleRoundModel,
)
from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.organization.domain.value_objects.organization import OrganizationId


class SqlAlchemySaleRoundRepository(AbstractSaleRoundRepository):
    """Async SQLAlchemy implementation of the SaleRound repository.

    Tenant-aware: every read is qualified by ``organization_id``. The
    repository never commits; the caller owns the transaction.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, sale_round: SaleRound) -> SaleRound:
        model = sale_round_entity_to_model(sale_round)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["created_at", "updated_at"])
        return sale_round_model_to_entity(model)

    async def get(
        self, organization_id: OrganizationId, id_: SaleRoundId
    ) -> SaleRound | None:
        stmt = select(SaleRoundModel).where(
            SaleRoundModel.id == id_.value,
            SaleRoundModel.organization_id == organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return sale_round_model_to_entity(model) if model is not None else None

    async def get_by_code(
        self, organization_id: OrganizationId, code: RoundCode
    ) -> SaleRound | None:
        stmt = select(SaleRoundModel).where(
            SaleRoundModel.organization_id == organization_id.value,
            SaleRoundModel.code == code.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return sale_round_model_to_entity(model) if model is not None else None

    async def list(self, organization_id: OrganizationId) -> Sequence[SaleRound]:
        stmt = (
            select(SaleRoundModel)
            .where(SaleRoundModel.organization_id == organization_id.value)
            .order_by(SaleRoundModel.created_at.desc())
        )
        models = (await self._session.scalars(stmt)).all()
        return [sale_round_model_to_entity(m) for m in models]

    async def save(self, sale_round: SaleRound) -> SaleRound | None:
        stmt = select(SaleRoundModel).where(
            SaleRoundModel.id == sale_round.id_.value,
            SaleRoundModel.organization_id == sale_round.organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        if model is None:
            return None
        apply_sale_round_to_model(sale_round, model)
        await self._session.flush()
        await self._session.refresh(model)
        return sale_round_model_to_entity(model)


class SqlAlchemyCampaignProductRepository(AbstractCampaignProductRepository):
    """Async SQLAlchemy implementation of the CampaignProduct repository.

    Scoped by ``organization_id`` (denormalized on each row). The repository
    never commits; the caller owns the transaction.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, campaign_product: CampaignProduct) -> CampaignProduct:
        model = campaign_product_entity_to_model(campaign_product)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["created_at", "updated_at"])
        return campaign_product_model_to_entity(model)

    async def get(
        self, organization_id: OrganizationId, id_: CampaignProductId
    ) -> CampaignProduct | None:
        stmt = select(CampaignProductModel).where(
            CampaignProductModel.id == id_.value,
            CampaignProductModel.organization_id == organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return campaign_product_model_to_entity(model) if model is not None else None

    async def get_by_round_and_product(
        self,
        organization_id: OrganizationId,
        sale_round_id: SaleRoundId,
        product_id: ProductId,
    ) -> CampaignProduct | None:
        stmt = select(CampaignProductModel).where(
            CampaignProductModel.organization_id == organization_id.value,
            CampaignProductModel.sale_round_id == sale_round_id.value,
            CampaignProductModel.product_id == product_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return campaign_product_model_to_entity(model) if model is not None else None

    async def list(
        self, organization_id: OrganizationId, sale_round_id: SaleRoundId
    ) -> Sequence[CampaignProduct]:
        stmt = (
            select(CampaignProductModel)
            .where(
                CampaignProductModel.organization_id == organization_id.value,
                CampaignProductModel.sale_round_id == sale_round_id.value,
            )
            .order_by(CampaignProductModel.created_at)
        )
        models = (await self._session.scalars(stmt)).all()
        return [campaign_product_model_to_entity(m) for m in models]

    async def save(
        self, campaign_product: CampaignProduct
    ) -> CampaignProduct | None:
        stmt = select(CampaignProductModel).where(
            CampaignProductModel.id == campaign_product.id_.value,
            CampaignProductModel.organization_id
            == campaign_product.organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        if model is None:
            return None
        apply_campaign_product_to_model(campaign_product, model)
        await self._session.flush()
        await self._session.refresh(model)
        return campaign_product_model_to_entity(model)
