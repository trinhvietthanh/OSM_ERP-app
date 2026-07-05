from src.modules.catalog.application.dto.product import (
    CreateProductInput,
    ProductRead,
)
from src.modules.catalog.application.exceptions import (
    ProductCodeAlreadyExistsError,
)
from src.modules.catalog.domain.entities.product import Product
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.domain.value_objects.product import (
    Description,
    ProductCode,
    ProductName,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId


class CreateProduct:
    """Create a new product in the caller's tenant, enforcing code uniqueness."""

    def __init__(self, repo: AbstractProductRepository) -> None:
        self._repo = repo

    async def execute(
        self, organization_id: OrganizationId, inp: CreateProductInput
    ) -> ProductRead:
        code = ProductCode(value=inp.code)
        if await self._repo.get_by_code(organization_id, code) is not None:
            raise ProductCodeAlreadyExistsError(inp.code)
        product = await self._repo.add(
            Product.create(
                organization_id=organization_id,
                code=code,
                name=ProductName(value=inp.name),
                description=Description(value=inp.description),
            )
        )
        return ProductRead.from_entity(product)
