from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.domain.value_objects.user import (
    Email,
    PasswordHash,
    UserId,
    UserRole,
    Username,
)
from src.modules.authenticate.infrastructure.models import UserModel
from src.modules.organization.domain.value_objects.organization import OrganizationId


def model_to_entity(model: UserModel) -> User:
    """Rebuild a domain User aggregate from a loaded ORM model."""
    return User(
        id_=UserId(value=model.id),
        organization_id=OrganizationId(value=model.organization_id),
        email=Email(value=model.email),
        username=Username(value=model.username),
        password_hash=PasswordHash(value=model.password_hash),
        role=model.role,
        is_active=model.is_active,
        created_at=model.created_at,
        updated_at=model.updated_at,
    )


def entity_to_model(entity: User) -> UserModel:
    """Build a new ORM model from a domain entity (for inserts)."""
    return UserModel(
        id=entity.id_.value,
        organization_id=entity.organization_id.value,
        email=entity.email.value,
        username=entity.username.value,
        password_hash=entity.password_hash.value,
        role=entity.role,
        is_active=entity.is_active,
    )
