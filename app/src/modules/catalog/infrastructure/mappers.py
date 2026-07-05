from src.modules.catalog.domain.entities.product import Product
from src.modules.catalog.domain.value_objects.product import (
    Description,
    ProductCode,
    ProductId,
    ProductName,
)
from src.modules.catalog.infrastructure.models import ProductModel
from src.modules.organization.domain.value_objects.organization import OrganizationId


def model_to_entity(model: ProductModel) -> Product:
    """Rebuild a domain Product aggregate from a loaded ORM model."""
    return Product(
        id_=ProductId(value=model.id),
        organization_id=OrganizationId(value=model.organization_id),
        code=ProductCode(value=model.code),
        name=ProductName(value=model.name),
        description=Description(value=model.description),
        is_active=model.active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def entity_to_model(entity: Product) -> ProductModel:
    """Build a new ORM model from a domain entity (for inserts)."""
    return ProductModel(
        id=entity.id_.value,
        organization_id=entity.organization_id.value,
        code=entity.code.value,
        name=entity.name.value,
        description=entity.description.value,
        active=entity.is_active,
    )


def apply_entity_to_model(entity: Product, model: ProductModel) -> None:
    """Copy mutable fields from *entity* onto a loaded *model* (for updates).

    ``id``, ``organization_id`` and ``code`` are immutable and intentionally
    not copied here.
    """
    model.name = entity.name.value
    model.description = entity.description.value
    model.active = entity.is_active
