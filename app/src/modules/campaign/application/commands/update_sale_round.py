from src.modules.campaign.application.dto.sale_round import (
    SaleRoundRead,
    UpdateSaleRoundInput,
)
from src.modules.campaign.application.exceptions import SaleRoundNotFoundError
from src.modules.campaign.domain.repository import AbstractSaleRoundRepository
from src.modules.campaign.domain.value_objects.sale_round import (
    RoundName,
    RoundStatus,
    SaleRoundId,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.shared.domain.base import DomainError


class UpdateSaleRound:
    """Apply a partial update to a sale round in the caller's tenant.

    ``name``/``status``/``opens_at``/``closes_at`` are each applied only when
    provided (a ``None`` value is treated as "not provided" in this MVP).
    """

    def __init__(self, repo: AbstractSaleRoundRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        organization_id: OrganizationId,
        id_: SaleRoundId,
        inp: UpdateSaleRoundInput,
    ) -> SaleRoundRead:
        sale_round = await self._repo.get(organization_id, id_)
        if sale_round is None:
            raise SaleRoundNotFoundError(id_)

        if inp.name is not None:
            sale_round.rename(RoundName(value=inp.name))
        if inp.status is not None:
            sale_round.change_status(self._parse_status(inp.status))
        if inp.opens_at is not None:
            sale_round.set_opens_at(inp.opens_at)
        if inp.closes_at is not None:
            sale_round.set_closes_at(inp.closes_at)

        updated = await self._repo.save(sale_round)
        assert updated is not None  # existence confirmed by get() above
        return SaleRoundRead.from_entity(updated)

    @staticmethod
    def _parse_status(raw: str) -> RoundStatus:
        try:
            return RoundStatus(raw)
        except ValueError as exc:
            raise DomainError(f"Invalid round status: {raw!r}.") from exc
