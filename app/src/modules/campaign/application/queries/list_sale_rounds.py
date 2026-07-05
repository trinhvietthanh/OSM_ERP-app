from src.modules.campaign.application.dto.sale_round import SaleRoundRead
from src.modules.campaign.domain.repository import AbstractSaleRoundRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId


class ListSaleRounds:
    """Return the caller's sale rounds, newest first."""

    def __init__(self, repo: AbstractSaleRoundRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId
    ) -> list[SaleRoundRead]:
        rounds = await self._repo.list(organization_id)
        return [SaleRoundRead.from_entity(r) for r in rounds]
