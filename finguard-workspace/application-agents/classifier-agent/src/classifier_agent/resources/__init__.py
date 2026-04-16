"""Dependency-injection factories for FastAPI ``Depends()``.

Each factory is a plain callable so tests can override them via
``app.dependency_overrides``. Singleton resources (LLMService, HTTP client
pool, checkpointer) are cached with ``functools.cache`` so a single instance
is shared across requests; per-request resources (DB sessions) use async
generators so FastAPI manages their lifecycle.
"""

from classifier_agent.resources.checkpointer import checkpointer_factory
from classifier_agent.resources.database import (
    engine_factory,
    get_db_session_factory,
    session_maker_factory,
)
from classifier_agent.resources.http_client import http_client_factory
from classifier_agent.resources.llm_service import llm_service_factory

__all__ = [
    "checkpointer_factory",
    "engine_factory",
    "get_db_session_factory",
    "http_client_factory",
    "llm_service_factory",
    "session_maker_factory",
]
