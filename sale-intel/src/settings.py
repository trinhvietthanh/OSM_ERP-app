from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Settings(BaseSettings):
    """Service configuration (env prefix ``SALEINTEL_``)."""

    model_config = SettingsConfigDict(
        env_prefix="SALEINTEL_", env_file=".env", extra="ignore"
    )

    database_url: str = (
        "postgresql+asyncpg://postgres:postgres@localhost:5432/sale_intel"
    )

    # Object storage
    storage_backend: str = "local"  # local | s3
    storage_local_root: Path = PROJECT_ROOT / "data" / "raw"
    s3_endpoint_url: str = "http://localhost:9000"
    s3_bucket: str = "sale-intel-raw"
    s3_access_key: str = "minioadmin"
    s3_secret_key: str = "minioadmin"

    # Crawling politeness. This service only reads public pages; it never
    # attempts captcha/anti-bot bypass, logins, or checkout automation.
    http_timeout_seconds: float = 30.0
    min_delay_seconds: float = 2.0
    user_agent: str = (
        "SaleIntelBot/0.1 (+contact: ops@example.com; respectful crawler)"
    )

    # Deal detection
    price_drop_threshold_pct: float = 10.0

    sources_config_dir: Path = PROJECT_ROOT / "configs" / "sources"


@lru_cache
def get_settings() -> Settings:
    return Settings()
