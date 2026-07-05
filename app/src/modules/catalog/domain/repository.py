import abc
from collections.abc import Sequence

from src.modules.catalog.domain.entities.product import Product
from src.modules.catalog.domain.value_objects.product import ProductCode, ProductId
from src.modules.organization.domain.value_objects.organization import OrganizationId


class AbstractProductRepository(abc.ABC):
    """Port for persisting Product aggregates, scoped to a tenant.

    Every read/write is qualified by ``organization_id`` so the data layer
    enforces tenant isolation: a caller can never fetch or mutate another
    tenant's product by guessing an id. Implementations live in the
    infrastructure layer. This interface depends only on domain types.
    """

    @abc.abstractmethod
    async def add(self, product: Product) -> Product:
        """Insert a new product and return the persisted aggregate."""
        ...

    @abc.abstractmethod
    async def get(
        self, organization_id: OrganizationId, id_: ProductId
    ) -> Product | None:
        """Return the tenant's product with *id_*, or ``None`` if not found."""
        ...

    @abc.abstractmethod
    async def get_by_code(
        self, organization_id: OrganizationId, code: ProductCode
    ) -> Product | None:
        """Return the tenant's product with *code*, or ``None`` if not found."""
        ...

    @abc.abstractmethod
    async def list(
        self, organization_id: OrganizationId, *, active_only: bool = True
    ) -> Sequence[Product]:
        """Return the tenant's products, optionally limited to active ones."""
        ...

    @abc.abstractmethod
    async def save(self, product: Product) -> Product | None:
        """Persist changes to an existing product; ``None`` if not found."""
        ...
