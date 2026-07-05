from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.infrastructure.postgres.health import check
from src.infrastructure.postgres.session import engine


@asynccontextmanager
async def postgres_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Startup: verify connectivity (fail-fast). Shutdown: dispose the engine.

    Compose this into the application's main lifespan, e.g.::

        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        from src.infrastructure.postgres.lifespan import postgres_lifespan

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            async with postgres_lifespan(app):
                yield

        app = FastAPI(lifespan=lifespan)
    """
    if not await check(engine):
        raise RuntimeError("Could not connect to Postgres on startup.")
    yield
    await engine.dispose()
