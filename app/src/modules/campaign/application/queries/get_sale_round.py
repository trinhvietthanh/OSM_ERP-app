from src.modules.campaign.application.dto.sale_round import SaleRoundRead
from src.modules.campaign.domain.repository import AbstractSaleRoundRepository
from src.modules.campaign.domain.value_objects.sale_round import SaleRoundId
from src.modules.organization.domain.value_objects.organization import OrganizationId


class GetSaleRound:
    """Return one sale round by id within the caller's tenant, or ``None``."""

    def __init__(self, repo: AbstractSaleRoundRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, id_: SaleRoundId
    ) -> SaleRoundRead | None:
        sale_round = await self._repo.get(organization_id, id_)
        if sale_round is None:
            return None
        return SaleRoundRead.from_entity(sale_round)
