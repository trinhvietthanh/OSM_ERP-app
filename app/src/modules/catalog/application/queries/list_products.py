from src.modules.catalog.application.dto.product import ProductRead
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.organization.domain.value_objects.organization import OrganizationId


class ListProducts:
    """Return the caller's products, optionally limited to active ones."""

    def __init__(self, repo: AbstractProductRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, *, active_only: bool = True
    ) -> list[ProductRead]:
        products = await self._repo.list(organization_id, active_only=active_only)
        return [ProductRead.from_entity(p) for p in products]
