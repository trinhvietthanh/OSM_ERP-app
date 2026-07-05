from src.modules.organization.domain.entities.organization import Organization
from src.modules.organization.domain.value_objects.organization import (
    OrganizationId,
    OrganizationName,
)
from src.modules.organization.infrastructure.models import OrganizationModel


def model_to_entity(model: OrganizationModel) -> Organization:
    """Rebuild a domain Organization aggregate from a loaded ORM model."""
    return Organization(
        id_=OrganizationId(value=model.id),
        name=OrganizationName(value=model.name),
        status=model.status,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def entity_to_model(entity: Organization) -> OrganizationModel:
    """Build a new ORM model from a domain entity (for inserts)."""
    return OrganizationModel(
        id=entity.id_.value,
        name=entity.name.value,
        status=entity.status,
    )


def apply_entity_to_model(entity: Organization, model: OrganizationModel) -> None:
    """Copy mutable fields from *entity* onto a loaded *model* (for updates)."""
    model.name = entity.name.value
    model.status = entity.status
