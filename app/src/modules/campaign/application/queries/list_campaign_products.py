from src.modules.campaign.application.dto.campaign_product import (
    CampaignProductRead,
)
from src.modules.campaign.domain.repository import AbstractCampaignProductRepository
from src.modules.campaign.domain.value_objects.sale_round import SaleRoundId
from src.modules.organization.domain.value_objects.organization import OrganizationId


class ListCampaignProducts:
    """Return the offerings of a sale round (within the caller's tenant)."""

    def __init__(self, repo: AbstractCampaignProductRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        organization_id: OrganizationId,
        sale_round_id: SaleRoundId,
    ) -> list[CampaignProductRead]:
        items = await self._repo.list(organization_id, sale_round_id)
        return [CampaignProductRead.from_entity(i) for i in items]
