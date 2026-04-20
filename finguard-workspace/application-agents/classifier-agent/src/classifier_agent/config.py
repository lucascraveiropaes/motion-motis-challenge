import os
from typing import Tuple, Type

from pydantic_settings import BaseSettings, PydanticBaseSettingsSource, TomlConfigSettingsSource


class Settings(BaseSettings):
    database_url: str = "sqlite+aiosqlite:///./classifier.db"

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: Type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: PydanticBaseSettingsSource,
        **kwargs
    ) -> Tuple[PydanticBaseSettingsSource, ...]:
        # Define the TOML configuration file
        toml_source = TomlConfigSettingsSource(settings_cls, toml_file=os.getenv("CONFIG_FILE", "config.toml"))
        return (init_settings, env_settings, toml_source)


settings = Settings()
