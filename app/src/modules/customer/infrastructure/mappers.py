from src.modules.customer.domain.entities.customer import Customer
from src.modules.customer.domain.value_objects.customer import (
    CustomerId,
    CustomerName,
    PhoneNumber,
)
from src.modules.customer.infrastructure.models import CustomerModel
from src.modules.organization.domain.value_objects.organization import OrganizationId


def customer_model_to_entity(model: CustomerModel) -> Customer:
    return Customer(
        id_=CustomerId(value=model.id),
        organization_id=OrganizationId(value=model.organization_id),
        name=CustomerName(value=model.name),
        phone=PhoneNumber(value=model.phone) if model.phone is not None else None,
        note=model.note,
        is_active=model.active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def customer_entity_to_model(entity: Customer) -> CustomerModel:
    return CustomerModel(
        id=entity.id_.value,
        organization_id=entity.organization_id.value,
        name=entity.name.value,
        phone=entity.phone.value if entity.phone is not None else None,
        note=entity.note,
        active=entity.is_active,
    )


def apply_customer_to_model(entity: Customer, model: CustomerModel) -> None:
    """Copy mutable fields. ``id``/``organization_id`` are immutable."""
    model.name = entity.name.value
    model.phone = entity.phone.value if entity.phone is not None else None
    model.note = entity.note
    model.active = entity.is_active
