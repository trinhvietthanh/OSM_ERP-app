import asyncio
import sys
from logging.config import fileConfig
from pathlib import Path

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

# Make `src` importable when alembic runs (env.py lives at <app>/migrations/).
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.infrastructure.postgres.base import Base  # noqa: E402
from src.infrastructure.postgres.settings import (  # noqa: E402
    get_postgres_settings,
)

# Import module ORM models so they register on ``Base.metadata`` before
# autogenerate runs. Add each module's models here as it gains persistence.
from src.modules.authenticate.infrastructure import models  # noqa: F401
from src.modules.campaign.infrastructure import models  # noqa: F401
from src.modules.catalog.infrastructure import models  # noqa: F401
from src.modules.customer.infrastructure import models  # noqa: F401
from src.modules.organization.infrastructure import models  # noqa: F401
from src.modules.purchase.infrastructure import models  # noqa: F401
from src.modules.trip.infrastructure import models  # noqa: F401

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Single migration target: the shared declarative metadata.
target_metadata = Base.metadata

_settings = get_postgres_settings()


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no DBAPI, no live connection).

    Calls to context.execute() here emit the given string to the script output.
    """
    context.configure(
        url=_settings.url.render_as_string(hide_password=False),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Create an async Engine and associate a connection with the context."""
    connectable = create_async_engine(_settings.url, poolclass=pool.NullPool)

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
