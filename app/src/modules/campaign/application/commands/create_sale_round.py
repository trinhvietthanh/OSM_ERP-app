from src.modules.campaign.application.dto.sale_round import (
    CreateSaleRoundInput,
    SaleRoundRead,
)
from src.modules.campaign.application.exceptions import (
    SaleRoundCodeAlreadyExistsError,
)
from src.modules.campaign.domain.entities.sale_round import SaleRound
from src.modules.campaign.domain.repository import AbstractSaleRoundRepository
from src.modules.campaign.domain.value_objects.sale_round import (
    RoundCode,
    RoundName,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId


class CreateSaleRound:
    """Create a new sale round in the caller's tenant, enforcing code uniqueness."""

    def __init__(self, repo: AbstractSaleRoundRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, inp: CreateSaleRoundInput
    ) -> SaleRoundRead:
        code = RoundCode(value=inp.code)
        if await self._repo.get_by_code(organization_id, code) is not None:
            raise SaleRoundCodeAlreadyExistsError(inp.code)
        sale_round = await self._repo.add(
            SaleRound.create(
                organization_id=organization_id,
                code=code,
                name=RoundName(value=inp.name),
            )
        )
        return SaleRoundRead.from_entity(sale_round)
