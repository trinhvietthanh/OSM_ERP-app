from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine


async def check(engine: AsyncEngine) -> bool:
    """Return ``True`` if a ``SELECT 1`` against *engine* succeeds, else ``False``.

    Never raises: intended for liveness probes and startup connectivity checks.
    """
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception:
        return False
    return True
