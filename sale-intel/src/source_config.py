"""Typed loader for the per-source YAML configs in ``configs/sources``."""

from pathlib import Path

import yaml
from pydantic import BaseModel

from src.settings import get_settings


class Entrypoint(BaseModel):
    url: str
    parser: str


class SourceConfig(BaseModel):
    source_id: str
    name: str
    country: str
    currency: str
    base_url: str
    crawl_type: str
    crawl_interval_minutes: int
    enabled: bool = True
    entrypoints: dict[str, Entrypoint] = {}


def load_source_config(path: Path) -> SourceConfig:
    with path.open() as fh:
        return SourceConfig.model_validate(yaml.safe_load(fh))


def load_all_source_configs() -> dict[str, SourceConfig]:
    """Return all configs keyed by source_id."""
    configs: dict[str, SourceConfig] = {}
    for path in sorted(get_settings().sources_config_dir.glob("*.yaml")):
        config = load_source_config(path)
        configs[config.source_id] = config
    return configs
