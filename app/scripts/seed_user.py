"""Seed a default organization (tenant) + admin user for local development.

Run after applying migrations::

    uv run alembic upgrade head
    uv run python scripts/seed_user.py

Idempotent: it skips records that already exist (matched by org name / email).
"""

import asyncio
import sys
from pathlib import Path

# Make `src` importable when run as a script from scripts/ (mirrors migrations/env.py).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sqlalchemy import select

from src.infrastructure.postgres.session import AsyncSessionFactory
from src.modules.authenticate.domain.entities.user import User
from src.modules.authenticate.domain.value_objects.user import (
    Email,
    PasswordHash,
    UserId,
    UserRole,
    Username,
)
from src.modules.authenticate.infrastructure.mappers import entity_to_model
from src.modules.authenticate.infrastructure.models import UserModel
from src.modules.authenticate.infrastructure.password_hasher import (
    BcryptPasswordHasher,
)
from src.modules.organization.domain.entities.organization import Organization
from src.modules.organization.domain.value_objects.organization import (
    OrganizationId,
    OrganizationName,
)
from src.modules.organization.infrastructure.models import OrganizationModel

ORG_NAME = "Default"
ADMIN_EMAIL = "admin@example.com"
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin12345"


async def main() -> None:
    hasher = BcryptPasswordHasher()
    async with AsyncSessionFactory() as session:
        org_stmt = select(OrganizationModel).where(OrganizationModel.name == ORG_NAME)
        org_model = (await session.scalars(org_stmt)).one_or_none()
        if org_model is None:
            org = Organization.create(name=OrganizationName(value=ORG_NAME))
            session.add(
                OrganizationModel(
                    id=org.id_.value, name=org.name.value, status=org.status
                )
            )
            # Flush so the org row exists in this transaction before we insert a
            # user that references it (otherwise the FK can be checked too early).
            await session.flush()
            org_id = org.id_.value
            print(f"[seed] Created organization {ORG_NAME!r} ({org_id}).")
        else:
            org_id = org_model.id
            print(f"[seed] Organization {ORG_NAME!r} already exists ({org_id}).")

        email_norm = ADMIN_EMAIL.strip().lower()
        user_stmt = select(UserModel).where(UserModel.email == email_norm)
        existing = (await session.scalars(user_stmt)).one_or_none()
        if existing is None:
            user = User(
                id_=UserId.generate(),
                organization_id=OrganizationId(value=org_id),
                email=Email.from_string(ADMIN_EMAIL),
                username=Username(value=ADMIN_USERNAME),
                password_hash=PasswordHash(value=hasher.hash(ADMIN_PASSWORD)),
                role=UserRole.ADMIN,
            )
            session.add(entity_to_model(user))
            print(
                f"[seed] Created admin user {ADMIN_EMAIL!r} "
                f"(password: {ADMIN_PASSWORD!r})."
            )
        else:
            print(f"[seed] User {ADMIN_EMAIL!r} already exists.")

        await session.commit()


if __name__ == "__main__":
    asyncio.run(main())
