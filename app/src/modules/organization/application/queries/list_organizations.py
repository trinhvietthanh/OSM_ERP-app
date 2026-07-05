from src.modules.organization.application.dto.organization import OrganizationRead
from src.modules.organization.domain.repository import AbstractOrganizationRepository


class ListOrganizations:
    """Return all organizations."""

    def __init__(self, repo: AbstractOrganizationRepository) -> None:
        self._repo = repo

    async def execute(self) -> list[OrganizationRead]:
        organizations = await self._repo.list()
        return [OrganizationRead.from_entity(o) for o in organizations]
