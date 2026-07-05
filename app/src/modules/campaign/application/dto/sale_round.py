from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from src.modules.campaign.domain.entities.sale_round import SaleRound


class CreateSaleRoundInput(BaseModel):
    """Payload for the CreateSaleRound command."""

    code: str
    name: str


class UpdateSaleRoundInput(BaseModel):
    """Partial payload for the UpdateSaleRound command. All fields optional."""

    name: str | None = None
    status: str | None = None  # "draft" | "open" | "closed"
    opens_at: datetime | None = None
    closes_at: datetime | None = None


class SaleRoundRead(BaseModel):
    """Read model returned by sale-round commands and queries."""

    id: UUID
    organization_id: UUID
    code: str
    name: str
    status: str
    opens_at: datetime | None = None
    closes_at: datetime | None = None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, sale_round: SaleRound) -> Self:
        return cls(
            id=sale_round.id_.value,
            organization_id=sale_round.organization_id.value,
            code=sale_round.code.value,
            name=sale_round.name.value,
            status=sale_round.status.value,
            opens_at=sale_round.opens_at,
            closes_at=sale_round.closes_at,
            created_at=sale_round.created_at,
            updated_at=sale_round.updated_at,
        )
