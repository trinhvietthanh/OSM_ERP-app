from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from src.modules.organization.domain.entities.organization import Organization


class OrganizationRead(BaseModel):
    """Read model returned by organization commands and queries."""

    id: UUID
    name: str
    status: str
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, organization: Organization) -> Self:
        return cls(
            id=organization.id_.value,
            name=organization.name.value,
            status=organization.status.value,
            created_at=organization.created_at,
            updated_at=organization.updated_at,
        )


class CreateOrganizationInput(BaseModel):
    """Payload for the CreateOrganization command."""

    name: str


class RenameOrganizationInput(BaseModel):
    """Payload for the RenameOrganization command."""

    name: str
