from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from src.modules.catalog.domain.entities.product import Product


class CreateProductInput(BaseModel):
    """Payload for the CreateProduct command."""

    code: str
    name: str
    description: str = ""


class UpdateProductInput(BaseModel):
    """Partial payload for the UpdateProduct command. All fields optional."""

    name: str | None = None
    description: str | None = None
    active: bool | None = None


class ProductRead(BaseModel):
    """Read model returned by catalog commands and queries."""

    id: UUID
    organization_id: UUID
    code: str
    name: str
    description: str
    active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, product: Product) -> Self:
        return cls(
            id=product.id_.value,
            organization_id=product.organization_id.value,
            code=product.code.value,
            name=product.name.value,
            description=product.description.value,
            active=product.is_active,
            created_at=product.created_at,
            updated_at=product.updated_at,
        )
