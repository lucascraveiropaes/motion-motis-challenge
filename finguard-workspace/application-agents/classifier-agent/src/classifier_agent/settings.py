"""Application settings loaded from TOML config files.

Picks the config file based on the ``FINGUARD_ENV`` environment variable
(defaulting to ``development``). The TOML file lives under
``src/config/<env>.toml`` relative to the installed package.

Environment variables with the ``FINGUARD_`` prefix override any value from
the TOML file, which lets us keep secrets out of version control while still
exposing sensible defaults for local dev.
"""

from __future__ import annotations

import os
import tomllib
from functools import cache
from pathlib import Path
from typing import Any

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


class AppSettings(BaseSettings):
    """Runtime configuration for the classifier agent."""

    model_config = SettingsConfigDict(
        env_prefix="FINGUARD_",
        env_nested_delimiter="__",
        extra="ignore",
    )

    environment: str = Field(default="development")
    database_url: str = Field(default="sqlite+aiosqlite:///./classifier.db")
    sync_database_url: str = Field(default="sqlite:///./classifier.db")
    checkpointer_backend: str = Field(default="memory")
    checkpointer_path: str = Field(default="./checkpoints.db")
    llm_backend: str = Field(default="rules")
    http_timeout_seconds: float = Field(default=10.0)


def _load_toml(env: str) -> dict[str, Any]:
    config_path = _CONFIG_DIR / f"{env}.toml"
    if not config_path.is_file():
        return {}
    with config_path.open("rb") as fh:
        return tomllib.load(fh)


@cache
def get_settings() -> AppSettings:
    """Return cached :class:`AppSettings` loaded from TOML + env vars.

    Precedence (highest to lowest): ``FINGUARD_*`` env vars → TOML file →
    class defaults. TOML values are merged on top of defaults and then
    env vars are applied last so deployments can override any TOML default.
    """
    env = os.environ.get("FINGUARD_ENV", "development")
    merged: dict[str, Any] = {"environment": env, **_load_toml(env)}
    for field_name in AppSettings.model_fields:
        env_key = f"FINGUARD_{field_name.upper()}"
        if env_key in os.environ:
            merged[field_name] = os.environ[env_key]
    return AppSettings(**merged)


def reset_settings_cache() -> None:
    """Clear the cached settings. Useful between test runs."""
    get_settings.cache_clear()
