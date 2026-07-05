from datetime import UTC, datetime
from typing import Self

from src.modules.customer.domain.value_objects.customer import (
    CustomerId,
    CustomerName,
    PhoneNumber,
)
from src.modules.organization.domain.value_objects.organization import OrganizationId
from src.shared.domain.base import Entity


class Customer(Entity[CustomerId]):
    """A shop's customer (the person placing pre-orders).

    Belongs to one tenant. Soft-deleted via ``is_active`` — orders keep
    referencing deactivated customers, so history is never lost.
    """

    def __init__(
        self,
        *,
        id_: CustomerId,
        organization_id: OrganizationId,
        name: CustomerName,
        phone: PhoneNumber | None = None,
        note: str = "",
        is_active: bool = True,
        created_at: datetime | None = None,
        updated_at: datetime | None = None,
    ) -> None:
        super().__init__(id_=id_)
        now = datetime.now(UTC)
        self._organization_id = organization_id
        self._name = name
        self._phone = phone
        self._note = note
        self._is_active = is_active
        self._created_at = created_at if created_at is not None else now
        self._updated_at = updated_at if updated_at is not None else now

    @classmethod
    def create(
        cls,
        *,
        organization_id: OrganizationId,
        name: CustomerName,
        phone: PhoneNumber | None = None,
        note: str = "",
    ) -> Self:
        """Factory: create a new active customer with a generated id."""
        return cls(
            id_=CustomerId.generate(),
            organization_id=organization_id,
            name=name,
            phone=phone,
            note=note,
        )

    @property
    def organization_id(self) -> OrganizationId:
        return self._organization_id

    @property
    def name(self) -> CustomerName:
        return self._name

    @property
    def phone(self) -> PhoneNumber | None:
        return self._phone

    @property
    def note(self) -> str:
        return self._note

    @property
    def is_active(self) -> bool:
        return self._is_active

    @property
    def created_at(self) -> datetime:
        return self._created_at

    @property
    def updated_at(self) -> datetime:
        return self._updated_at

    def rename(self, new_name: CustomerName) -> None:
        """Rename the customer. No-op if unchanged."""
        if new_name == self._name:
            return
        self._name = new_name
        self._touch()

    def change_phone(self, new_phone: PhoneNumber | None) -> None:
        """Set (or clear) the phone number. No-op if unchanged."""
        if new_phone == self._phone:
            return
        self._phone = new_phone
        self._touch()

    def change_note(self, new_note: str) -> None:
        """Replace the free-text note. No-op if unchanged."""
        if new_note == self._note:
            return
        self._note = new_note
        self._touch()

    def activate(self) -> None:
        if self._is_active:
            return
        self._is_active = True
        self._touch()

    def deactivate(self) -> None:
        if not self._is_active:
            return
        self._is_active = False
        self._touch()

    def _touch(self) -> None:
        """Refresh updated_at to reflect a mutation."""
        self._updated_at = datetime.now(UTC)
