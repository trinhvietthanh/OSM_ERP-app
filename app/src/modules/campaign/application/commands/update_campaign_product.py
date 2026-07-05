from src.modules.campaign.application.dto.campaign_product import (
    CampaignProductRead,
    UpdateCampaignProductInput,
)
from src.modules.campaign.application.exceptions import (
    CampaignProductNotFoundError,
)
from src.modules.campaign.domain.repository import AbstractCampaignProductRepository
from src.modules.campaign.domain.value_objects.campaign_product import (
    CampaignProductId,
    Money,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId


class UpdateCampaignProduct:
    """Apply a partial update to a campaign product (price / deposit)."""

    def __init__(self, repo: AbstractCampaignProductRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        organization_id: OrganizationId,
        id_: CampaignProductId,
        inp: UpdateCampaignProductInput,
    ) -> CampaignProductRead:
        campaign_product = await self._repo.get(organization_id, id_)
        if campaign_product is None:
            raise CampaignProductNotFoundError(id_)

        if inp.price is not None:
            campaign_product.change_price(Money(amount=inp.price))
        if inp.deposit is not None:
            campaign_product.change_deposit(Money(amount=inp.deposit))

        updated = await self._repo.save(campaign_product)
        assert updated is not None  # existence confirmed by get() above
        return CampaignProductRead.from_entity(updated)
