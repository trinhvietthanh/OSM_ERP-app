from src.modules.campaign.domain.entities.campaign_product import CampaignProduct
from src.modules.campaign.domain.entities.sale_round import SaleRound
from src.modules.campaign.domain.value_objects.campaign_product import (
    CampaignProductId,
    Money,
)
from src.modules.campaign.domain.value_objects.sale_round import (
    RoundCode,
    RoundName,
    SaleRoundId,
)
from src.modules.campaign.infrastructure.models import (
    CampaignProductModel,
    SaleRoundModel,
)
from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.organization.domain.value_objects.organization import OrganizationId


# --- SaleRound ---


def sale_round_model_to_entity(model: SaleRoundModel) -> SaleRound:
    return SaleRound(
        id_=SaleRoundId(value=model.id),
        organization_id=OrganizationId(value=model.organization_id),
        code=RoundCode(value=model.code),
        name=RoundName(value=model.name),
        status=model.status,
        opens_at=model.opens_at,
        closes_at=model.closes_at,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def sale_round_entity_to_model(entity: SaleRound) -> SaleRoundModel:
    return SaleRoundModel(
        id=entity.id_.value,
        organization_id=entity.organization_id.value,
        code=entity.code.value,
        name=entity.name.value,
        status=entity.status,
        opens_at=entity.opens_at,
        closes_at=entity.closes_at,
    )


def apply_sale_round_to_model(entity: SaleRound, model: SaleRoundModel) -> None:
    """Copy mutable fields. ``id``/``organization_id``/``code`` are immutable."""
    model.name = entity.name.value
    model.status = entity.status
    model.opens_at = entity.opens_at
    model.closes_at = entity.closes_at


# --- CampaignProduct ---


def campaign_product_model_to_entity(model: CampaignProductModel) -> CampaignProduct:
    return CampaignProduct(
        id_=CampaignProductId(value=model.id),
        organization_id=OrganizationId(value=model.organization_id),
        sale_round_id=SaleRoundId(value=model.sale_round_id),
        product_id=ProductId(value=model.product_id),
        price=Money(amount=model.price),
        deposit=Money(amount=model.deposit),
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def campaign_product_entity_to_model(entity: CampaignProduct) -> CampaignProductModel:
    return CampaignProductModel(
        id=entity.id_.value,
        organization_id=entity.organization_id.value,
        sale_round_id=entity.sale_round_id.value,
        product_id=entity.product_id.value,
        price=entity.price.amount,
        deposit=entity.deposit.amount,
    )


def apply_campaign_product_to_model(
    entity: CampaignProduct, model: CampaignProductModel
) -> None:
    """Copy mutable fields. ``sale_round_id``/``product_id`` are immutable."""
    model.price = entity.price.amount
    model.deposit = entity.deposit.amount
