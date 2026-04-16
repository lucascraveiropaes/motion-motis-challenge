"""Shared test fixtures.

We build a self-contained SQLite DB (file-backed so both the async driver
used by the app and the sync driver used by the black-box tests see the
same rows) per test, wire it into the app through
``app.dependency_overrides`` and hand the test a live ``AsyncClient`` plus a
sync ``db_session`` view on the same data.
"""

from __future__ import annotations

import asyncio
from collections.abc import AsyncIterator, Iterator
from pathlib import Path

import httpx
import pytest
import pytest_asyncio
from classifier_agent.app import app
from classifier_agent.models import Base
from classifier_agent.resources import (
    get_db_session_factory,
    http_client_factory,
    llm_service_factory,
)
from classifier_agent.services.llm_service import RuleBasedLLMService
from httpx import ASGITransport, AsyncClient
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import Session, sessionmaker


@pytest.fixture(scope="session")
def event_loop() -> Iterator[asyncio.AbstractEventLoop]:
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sqlite_path(tmp_path: Path) -> Path:
    return tmp_path / "test.db"


@pytest_asyncio.fixture
async def async_engine(sqlite_path: Path):
    engine = create_async_engine(f"sqlite+aiosqlite:///{sqlite_path}")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def async_session_maker(async_engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(async_engine, expire_on_commit=False, class_=AsyncSession)


@pytest.fixture
def sync_engine(sqlite_path: Path, async_engine):
    _ = async_engine  # ensure schema is created before the sync engine opens
    engine = create_engine(f"sqlite:///{sqlite_path}")
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(sync_engine) -> Iterator[Session]:
    SessionLocal = sessionmaker(bind=sync_engine, autoflush=False, autocommit=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@pytest_asyncio.fixture
async def client(async_session_maker) -> AsyncIterator[AsyncClient]:
    async def _override_session() -> AsyncIterator[AsyncSession]:
        async with async_session_maker() as session:
            yield session

    async def _override_http() -> AsyncIterator[httpx.AsyncClient]:
        async with httpx.AsyncClient(timeout=1.0) as c:
            yield c

    def _override_llm() -> RuleBasedLLMService:
        return RuleBasedLLMService()

    app.dependency_overrides[get_db_session_factory] = _override_session
    app.dependency_overrides[http_client_factory] = _override_http
    app.dependency_overrides[llm_service_factory] = _override_llm

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as c:
        yield c

    app.dependency_overrides.clear()
