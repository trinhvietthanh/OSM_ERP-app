from datetime import UTC, datetime
from typing import Self

from src.modules.campaign.domain.value_objects.sale_round import (
    RoundCode,
    RoundName,
    RoundStatus,
    SaleRoundId,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.shared.domain.base import Entity


class SaleRound(Entity[SaleRoundId]):
    """A pre-order campaign (a "đợt sale").

    Groups the products offered together for a period. Belongs to one tenant.
    The round itself carries no prices — each offered product's price/deposit
    lives on a :class:`CampaignProduct`. ``code`` and tenant are immutable;
    ``name``/``status``/``opens_at``/``closes_at`` are editable.
    """

    def __init__(
        self,
        *,
        id_: SaleRoundId,
        organization_id: OrganizationId,
        code: RoundCode,
        name: RoundName,
        status: RoundStatus = RoundStatus.DRAFT,
        opens_at: datetime | None = None,
        closes_at: datetime | None = None,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        now = datetime.now(UTC)
        self._organization_id = organization_id
        self._code = code
        self._name = name
        self._status = status
        self._opens_at = opens_at
        self._closes_at = closes_at
        self._created_at = created_at if created_at is not None else now
        self._updated_at = updated_at if updated_at is not None else now

    @classmethod
    def create(
        cls,
        *,
        organization_id: OrganizationId,
        code: RoundCode,
        name: RoundName,
    ) -> Self:
        """Factory: create a new round in DRAFT with a generated id."""
        return cls(
            id_=SaleRoundId.generate(),
            organization_id=organization_id,
            code=code,
            name=name,
        )

    @property
    def organization_id(self) -> OrganizationId:
        return self._organization_id

    @property
    def code(self) -> RoundCode:
        return self._code

    @property
    def name(self) -> RoundName:
        return self._name

    @property
    def status(self) -> RoundStatus:
        return self._status

    @property
    def opens_at(self) -> datetime | None:
        return self._opens_at

    @property
    def closes_at(self) -> datetime | None:
        return self._closes_at

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def rename(self, new_name: RoundName) -> None:
        """Rename the round. No-op if unchanged."""
        if new_name == self._name:
            return
        self._name = new_name
        self._touch()

    def change_status(self, new_status: RoundStatus) -> None:
        """Set the lifecycle status. No-op if unchanged."""
        if new_status == self._status:
            return
        self._status = new_status
        self._touch()

    def set_opens_at(self, opens_at: datetime | None) -> None:
        """Set (or clear) the opening timestamp. No-op if unchanged."""
        if opens_at == self._opens_at:
            return
        self._opens_at = opens_at
        self._touch()

    def set_closes_at(self, closes_at: datetime | None) -> None:
        """Set (or clear) the closing timestamp. No-op if unchanged."""
        if closes_at == self._closes_at:
            return
        self._closes_at = closes_at
        self._touch()

    def _touch(self) -> None:
        """Refresh updated_at to reflect a mutation."""
        self._updated_at = datetime.now(UTC)
