"""Tests for DI factories and settings."""

from __future__ import annotations

import httpx
import pytest
from classifier_agent.resources.checkpointer import checkpointer_factory
from classifier_agent.resources.database import (
    engine_factory,
    get_db_session_factory,
    reset_database_cache,
    session_maker_factory,
)
from classifier_agent.resources.http_client import http_client_factory
from classifier_agent.resources.llm_service import llm_service_factory
from classifier_agent.services.llm_service import LLMService
from classifier_agent.settings import AppSettings, get_settings, reset_settings_cache
from langgraph.checkpoint.memory import MemorySaver


def test_llm_service_factory_returns_llm_service() -> None:
    llm_service_factory.cache_clear()
    svc = llm_service_factory()
    assert isinstance(svc, LLMService)


def test_llm_service_factory_unknown_backend_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    llm_service_factory.cache_clear()
    reset_settings_cache()
    monkeypatch.setenv("FINGUARD_LLM_BACKEND", "unknown-backend")
    svc = llm_service_factory()
    assert isinstance(svc, LLMService)
    llm_service_factory.cache_clear()
    reset_settings_cache()


def test_checkpointer_factory_defaults_to_memory() -> None:
    checkpointer_factory.cache_clear()
    saver = checkpointer_factory()
    assert isinstance(saver, MemorySaver)


@pytest.mark.asyncio
async def test_http_client_factory_yields_async_client() -> None:
    async for client in http_client_factory():
        assert isinstance(client, httpx.AsyncClient)
        break


@pytest.mark.asyncio
async def test_get_db_session_factory_yields_session(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:
    reset_database_cache()
    reset_settings_cache()
    db_path = tmp_path / "factory.db"
    monkeypatch.setenv("FINGUARD_DATABASE_URL", f"sqlite+aiosqlite:///{db_path}")
    try:
        from classifier_agent.resources.database import init_models

        await init_models()
        session_gen = get_db_session_factory()
        session = await session_gen.__anext__()
        assert session is not None
        await session.close()
        try:
            await session_gen.__anext__()
        except StopAsyncIteration:
            pass
    finally:
        engine = engine_factory()
        await engine.dispose()
        reset_database_cache()
        reset_settings_cache()


def test_session_maker_factory_is_cached() -> None:
    reset_database_cache()
    first = session_maker_factory()
    second = session_maker_factory()
    assert first is second
    reset_database_cache()


def test_settings_reads_env_overrides(monkeypatch: pytest.MonkeyPatch) -> None:
    reset_settings_cache()
    monkeypatch.setenv("FINGUARD_LLM_BACKEND", "rules")
    monkeypatch.setenv("FINGUARD_HTTP_TIMEOUT_SECONDS", "7.5")
    settings = get_settings()
    assert isinstance(settings, AppSettings)
    assert settings.http_timeout_seconds == 7.5
    reset_settings_cache()
