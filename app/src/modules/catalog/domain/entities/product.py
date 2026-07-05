from datetime import UTC, datetime
from typing import Self

from src.modules.catalog.domain.value_objects.product import (
    Description,
    ProductCode,
    ProductId,
    ProductName,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.shared.domain.base import Entity


class Product(Entity[ProductId]):
    """A sellable item in a tenant's catalog.

    Belongs to exactly one organization (the ERP tenant). The product carries
    **no price** — pricing depends on the sale round and lives on a
    ``CampaignProduct``. ``code`` and tenant are immutable after creation;
    ``name``/``description`` are editable and the product can be deactivated
    (soft-deleted) and reactivated.
    """

    def __init__(
        self,
        *,
        id_: ProductId,
        organization_id: OrganizationId,
        code: ProductCode,
        name: ProductName,
        description: Description,
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        now = datetime.now(UTC)
        self._organization_id = organization_id
        self._code = code
        self._name = name
        self._description = description
        self._is_active = is_active
        self._created_at = created_at if created_at is not None else now
        self._updated_at = updated_at if updated_at is not None else now

    @classmethod
    def create(
        cls,
        *,
        organization_id: OrganizationId,
        code: ProductCode,
        name: ProductName,
        description: Description,
    ) -> Self:
        """Factory: create a new active product with a generated id."""
        return cls(
            id_=ProductId.generate(),
            organization_id=organization_id,
            code=code,
            name=name,
            description=description,
        )

    @property
    def organization_id(self) -> OrganizationId:
        return self._organization_id

    @property
    def code(self) -> ProductCode:
        return self._code

    @property
    def name(self) -> ProductName:
        return self._name

    @property
    def description(self) -> Description:
        return self._description

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def rename(self, new_name: ProductName) -> None:
        """Rename the product. No-op if the name is unchanged."""
        if new_name == self._name:
            return
        self._name = new_name
        self._touch()

    def change_description(self, new_description: Description) -> None:
        """Replace the description. No-op if unchanged."""
        if new_description == self._description:
            return
        self._description = new_description
        self._touch()

    def activate(self) -> None:
        """Reactivate the product. Idempotent."""
        if self._is_active:
            return
        self._is_active = True
        self._touch()

    def deactivate(self) -> None:
        """Soft-delete (deactivate) the product. Idempotent."""
        if not self._is_active:
            return
        self._is_active = False
        self._touch()

    def _touch(self) -> None:
        """Refresh updated_at to reflect a mutation."""
        self._updated_at = datetime.now(UTC)
