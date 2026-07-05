from src.modules.organization.application.dto.organization import OrganizationRead
from src.modules.organization.application.exceptions import OrganizationNotFoundError
from src.modules.organization.domain.repository import AbstractOrganizationRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId


class SuspendOrganization:
    """Suspend an existing organization (idempotent)."""

    def __init__(self, repo: AbstractOrganizationRepository) -> None:
        self._repo = repo

    async def execute(self, id_: OrganizationId) -> OrganizationRead:
        organization = await self._repo.get(id_)
        if organization is None:
            raise OrganizationNotFoundError(id_)
        organization.suspend()
        updated = await self._repo.save(organization)
        assert updated is not None  # existence confirmed by get() above
        return OrganizationRead.from_entity(updated)
