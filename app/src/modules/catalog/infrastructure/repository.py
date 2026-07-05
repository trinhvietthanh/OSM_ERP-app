from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.modules.catalog.domain.entities.product import Product
from src.modules.catalog.domain.repository import AbstractProductRepository
from src.modules.catalog.domain.value_objects.product import ProductCode, ProductId
from src.modules.catalog.infrastructure.mappers import (
    apply_entity_to_model,
    entity_to_model,
    model_to_entity,
)
from src.modules.catalog.infrastructure.models import ProductModel
from src.modules.organization.domain.value_objects.organization import OrganizationId


class SqlAlchemyProductRepository(AbstractProductRepository):
    """Async SQLAlchemy implementation of the Product repository.

    Tenant-aware: every read is qualified by ``organization_id``. The
    repository never commits; the caller owns the transaction.
    """

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def add(self, product: Product) -> Product:
        model = entity_to_model(product)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model, attribute_names=["created_at", "updated_at"])
        return model_to_entity(model)

    async def get(
        self, organization_id: OrganizationId, id_: ProductId
    ) -> Product | None:
        stmt = select(ProductModel).where(
            ProductModel.id == id_.value,
            ProductModel.organization_id == organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return model_to_entity(model) if model is not None else None

    async def get_by_code(
        self, organization_id: OrganizationId, code: ProductCode
    ) -> Product | None:
        stmt = select(ProductModel).where(
            ProductModel.organization_id == organization_id.value,
            ProductModel.code == code.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        return model_to_entity(model) if model is not None else None

    async def list(
        self, organization_id: OrganizationId, *, active_only: bool = True
    ) -> Sequence[Product]:
        stmt = select(ProductModel).where(
            ProductModel.organization_id == organization_id.value
        )
        if active_only:
            stmt = stmt.where(ProductModel.active.is_(True))
        stmt = stmt.order_by(ProductModel.name)
        models = (await self._session.scalars(stmt)).all()
        return [model_to_entity(m) for m in models]

    async def save(self, product: Product) -> Product | None:
        stmt = select(ProductModel).where(
            ProductModel.id == product.id_.value,
            ProductModel.organization_id == product.organization_id.value,
        )
        model = (await self._session.scalars(stmt)).one_or_none()
        if model is None:
            return None
        apply_entity_to_model(product, model)
        await self._session.flush()
        await self._session.refresh(model)
        return model_to_entity(model)
