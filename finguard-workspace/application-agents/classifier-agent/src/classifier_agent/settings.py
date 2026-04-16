from functools import lru_cache
from pathlib import Path
from typing import Any

from pydantic_settings import (
    BaseSettings,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
    TomlConfigSettingsSource,
)

_CONFIG_FILE = Path(__file__).parent.parent / "config" / "settings.toml"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        **kwargs: Any,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        return (
            kwargs["init_settings"],
            kwargs["env_settings"],
            kwargs["dotenv_settings"],
            TomlConfigSettingsSource(settings_cls, toml_file=_CONFIG_FILE),
        )

    # Database — secrets from .env, defaults from settings.toml
    db_user: str = "motion"
    db_password: str = "motion"
    db_host: str = "localhost"
    db_port: int = 5432
    db_name: str = "motion"

    # OpenAI — API key from .env, model config from settings.toml
    openai_api_key: str = ""
    openai_model: str = "gpt-4o-mini"
    openai_temperature: int = 0


@lru_cache
def get_settings() -> Settings:
    return Settings()
