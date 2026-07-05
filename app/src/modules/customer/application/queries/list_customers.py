from src.modules.customer.application.dto.customer import CustomerRead
from src.modules.customer.domain.repository import AbstractCustomerRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId


class ListCustomers:
    """List the tenant's customers, optionally filtered by a search term."""

    def __init__(self, repo: AbstractCustomerRepository) -> None:
        self._repo = repo

    async def execute(
        self,
        organization_id: OrganizationId,
        search: str | None = None,
        active_only: bool = True,
    ) -> list[CustomerRead]:
        customers = await self._repo.list(
            organization_id, search=search, active_only=active_only
        )
        return [CustomerRead.from_entity(c) for c in customers]
