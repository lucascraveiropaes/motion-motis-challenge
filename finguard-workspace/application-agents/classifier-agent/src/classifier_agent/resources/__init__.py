import os
import tomllib
from collections.abc import Generator
from dataclasses import dataclass
from functools import cache
from pathlib import Path

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from classifier_agent.models import Base
from classifier_agent.resources.checkpointer import (
    Checkpointer,
    InMemoryCheckpointer,
    SqlAlchemyCheckpointer,
    resolve_checkpointer_backend,
)
from classifier_agent.resources.http_client import http_client_factory
from classifier_agent.resources.llm_service import LLMService, llm_service_factory

load_dotenv(dotenv_path=Path(__file__).resolve().parents[3] / ".env")


@dataclass(frozen=True)
class AppSettings:
    database_url: str


def _load_config_file() -> dict[str, str]:
    env = os.getenv("APP_ENV", "base").lower()
    config_dir = Path(__file__).resolve().parents[2] / "config"
    filename = "production.toml" if env in {"prod", "production"} else "base.toml"

    with (config_dir / filename).open("rb") as config_file:
        return tomllib.load(config_file)


@cache
def get_settings() -> AppSettings:
    config = _load_config_file()
    db_url = os.getenv("DATABASE_URL", config.get("database_url", ""))
    if not db_url:
        raise RuntimeError("DATABASE_URL is not configured")

    return AppSettings(database_url=db_url)


@cache
def get_engine():
    engine = create_engine(get_settings().database_url)
    Base.metadata.create_all(bind=engine)
    return engine


@cache
def get_session_maker() -> sessionmaker[Session]:
    return sessionmaker(autocommit=False, autoflush=False, bind=get_engine())


def get_db_session_factory() -> Generator[Session, None, None]:
    session = get_session_maker()()
    try:
        yield session
    finally:
        session.close()


@cache
def checkpointer_factory() -> Checkpointer:
    backend = resolve_checkpointer_backend(get_settings().database_url)
    if backend in {"sqlite", "postgres"}:
        return SqlAlchemyCheckpointer(get_engine())

    return InMemoryCheckpointer()


__all__ = [
    "AppSettings",
    "Checkpointer",
    "LLMService",
    "checkpointer_factory",
    "get_db_session_factory",
    "get_engine",
    "get_session_maker",
    "get_settings",
    "http_client_factory",
    "llm_service_factory",
]
