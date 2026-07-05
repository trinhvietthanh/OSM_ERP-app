from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Global declarative base for all ORM models across modules.

    ``Base.metadata`` is the single migration target used by Alembic
    (see ``migrations/env.py``): every module's ORM models subclass ``Base``
    so their tables register on one shared metadata.
    """


class TimestampMixin:
    """Mixin adding ``created_at`` / ``updated_at`` columns managed by the DB."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
