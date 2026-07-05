from src.modules.campaign.application.dto.campaign_product import (
    CampaignProductRead,
)
from src.modules.campaign.domain.repository import AbstractCampaignProductRepository
from src.modules.campaign.domain.value_objects.campaign_product import (
    CampaignProductId,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId


class GetCampaignProduct:
    """Return one campaign product by id within the caller's tenant, or ``None``."""

    def __init__(self, repo: AbstractCampaignProductRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, id_: CampaignProductId
    ) -> CampaignProductRead | None:
        campaign_product = await self._repo.get(organization_id, id_)
        if campaign_product is None:
            return None
        return CampaignProductRead.from_entity(campaign_product)
