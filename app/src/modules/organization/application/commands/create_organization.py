from src.modules.organization.application.dto.organization import (
    CreateOrganizationInput,
    OrganizationRead,
)
from src.modules.organization.application.exceptions import (
    OrganizationAlreadyExistsError,
)
from src.modules.organization.domain.entities.organization import Organization
from src.modules.organization.domain.repository import AbstractOrganizationRepository
from src.modules.organization.domain.value_objects.organization import OrganizationName


class CreateOrganization:
    """Create a new organization, enforcing name uniqueness."""

    def __init__(self, repo: AbstractOrganizationRepository) -> None:
        self._repo = repo

    async def execute(self, inp: CreateOrganizationInput) -> OrganizationRead:
        name = OrganizationName(value=inp.name)
        if await self._repo.get_by_name(name) is not None:
            raise OrganizationAlreadyExistsError(inp.name)
        organization = await self._repo.add(Organization.create(name=name))
        return OrganizationRead.from_entity(organization)
