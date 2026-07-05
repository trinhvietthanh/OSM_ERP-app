from src.modules.catalog.application.dto.product import ProductRead
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.domain.value_objects.product import ProductId
from src.modules.organization.domain.value_objects.organization import OrganizationId


class GetProduct:
    """Return one product by id within the caller's tenant, or ``None``."""

    def __init__(self, repo: AbstractProductRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, id_: ProductId
    ) -> ProductRead | None:
        product = await self._repo.get(organization_id, id_)
        if product is None:
            return None
        return ProductRead.from_entity(product)
