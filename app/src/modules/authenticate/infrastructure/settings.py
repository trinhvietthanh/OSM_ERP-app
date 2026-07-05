from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class JwtSettings(BaseSettings):
    """JWT signing settings, loaded from the environment.

    Environment variables use the ``JWT_`` prefix (e.g. ``JWT_SECRET``) and may
    be supplied through a ``.env`` file at the app root. ``secret`` has no
    default on purpose so a missing secret fails fast rather than silently
    signing tokens with a known value.
    """

    model_config = SettingsConfigDict(
        env_prefix="JWT_",
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    secret: str
    algorithm: str = "HS256"
    access_expire_minutes: int = 60


@lru_cache
def get_jwt_settings() -> JwtSettings:
    """Return a process-wide cached :class:`JwtSettings` instance."""
    return JwtSettings()
