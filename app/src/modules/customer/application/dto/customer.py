from datetime import datetime
from typing import Self
from uuid import UUID

from pydantic import BaseModel

from src.modules.customer.domain.entities.customer import Customer


class CreateCustomerInput(BaseModel):
    """Payload for the CreateCustomer command."""

    name: str
    phone: str | None = None
    note: str = ""


class UpdateCustomerInput(BaseModel):
    """Partial payload for the UpdateCustomer command. All fields optional.

    ``phone=""`` clears the phone; ``phone=None`` (omitted) leaves it unchanged.
    """

    name: str | None = None
    phone: str | None = None
    note: str | None = None
    active: bool | None = None


class CustomerRead(BaseModel):
    """Read model returned by customer commands and queries."""

    id: UUID
    organization_id: UUID
    name: str
    phone: str | None = None
    note: str
    active: bool
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_entity(cls, customer: Customer) -> Self:
        return cls(
            id=customer.id_.value,
            organization_id=customer.organization_id.value,
            name=customer.name.value,
            phone=customer.phone.value if customer.phone is not None else None,
            note=customer.note,
            active=customer.is_active,
            created_at=customer.created_at,
            updated_at=customer.updated_at,
        )
