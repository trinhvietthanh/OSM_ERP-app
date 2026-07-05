from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class PostgresSettings(BaseSettings):
    """Postgres connection and pool settings, loaded from the environment.

    Environment variables use the ``POSTGRES_`` prefix (e.g. ``POSTGRES_HOST``)
    and may be supplied through a ``.env`` file at the app root.
    """

    model_config = SettingsConfigDict(
        env_prefix="POSTGRES_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    host: str = "localhost"
    port: int = 5432
    user: str = "postgres"
    password: str = ""
    db: str = "app"
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: float = 30.0
    pool_recycle: int = 1800
    echo: bool = False

    @property
    def url(self) -> URL:
        """Async SQLAlchemy URL (``postgresql+asyncpg``).

        Pass this directly to ``create_async_engine``. Avoid stringifying and
        re-parsing it: ``str(url)`` masks the password in SQLAlchemy 2.0, and a
        string round-trip can mangle special characters in credentials.
        """
        return URL.create(
            drivername="postgresql+asyncpg",
            username=self.user,
            password=self.password,
            host=self.host,
            port=self.port,
            database=self.db,
        )


@lru_cache
def get_postgres_settings() -> PostgresSettings:
    """Return a process-wide cached :class:`PostgresSettings` instance."""
    return PostgresSettings()
