from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from src.infrastructure.postgres.settings import get_postgres_settings

_settings = get_postgres_settings()

engine: AsyncEngine = create_async_engine(
    _settings.url,
    pool_size=_settings.pool_size,
    max_overflow=_settings.max_overflow,
    pool_timeout=_settings.pool_timeout,
    pool_recycle=_settings.pool_recycle,
    echo=_settings.echo,
    future=True,
)

AsyncSessionFactory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    autoflush=False,
    class_=AsyncSession,
)


async def get_session() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency yielding a request-scoped :class:`AsyncSession`.

    Unit-of-work per request: commits on success, rolls back on error. Use
    cases only ``flush`` (never commit); this is the single commit boundary, so
    every successful request persists its writes and any failure is atomic.
    """
    async with AsyncSessionFactory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
