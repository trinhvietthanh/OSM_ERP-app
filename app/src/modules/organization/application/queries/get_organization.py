from src.modules.organization.application.dto.organization import OrganizationRead
from src.modules.organization.domain.repository import AbstractOrganizationRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId


class GetOrganization:
    """Return one organization by id, or ``None`` if not found."""

    def __init__(self, repo: AbstractOrganizationRepository) -> None:
        self._repo = repo

    async def execute(self, id_: OrganizationId) -> OrganizationRead | None:
        organization = await self._repo.get(id_)
        if organization is None:
            return None
        return OrganizationRead.from_entity(organization)
