from datetime import datetime
from decimal import Decimal
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from src.modules.campaign.domain.entities.campaign_product import CampaignProduct


class CreateCampaignProductInput(BaseModel):
    """Payload for the CreateCampaignProduct command.

    ``sale_round_id`` comes from the URL path, not the body.
    """

    product_id: UUID
    price: Decimal
    deposit: Decimal


class UpdateCampaignProductInput(BaseModel):
    """Partial payload for the UpdateCampaignProduct command. All optional."""

    price: Decimal | None = None
    deposit: Decimal | None = None


class CampaignProductRead(BaseModel):
    """Read model returned by campaign-product commands and queries."""

    id: UUID
    organization_id: UUID
    sale_round_id: UUID
    product_id: UUID
    price: Decimal
    deposit: Decimal
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, campaign_product: CampaignProduct) -> Self:
        return cls(
            id=campaign_product.id_.value,
            organization_id=campaign_product.organization_id.value,
            sale_round_id=campaign_product.sale_round_id.value,
            product_id=campaign_product.product_id.value,
            price=campaign_product.price.amount,
            deposit=campaign_product.deposit.amount,
            created_at=campaign_product.created_at,
            updated_at=campaign_product.updated_at,
        )
