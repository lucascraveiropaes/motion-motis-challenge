import pytest
from classifier_agent.config import settings
from classifier_agent.resources.database import get_db_session_factory
from classifier_agent.resources.services import checkpointer_factory
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_read_root(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to the FinGuard Classifier Agent!"}


@pytest.mark.asyncio
async def test_db_session_factory():
    gen = get_db_session_factory()
    session = await anext(gen)
    assert session is not None
    try:
        await anext(gen)
    except StopAsyncIteration:
        pass


@pytest.mark.asyncio
async def test_checkpointer_factory_postgres(monkeypatch):
    monkeypatch.setattr(settings, "database_url", "postgresql://user:pass@localhost/db")
    gen = checkpointer_factory()
    chk = await anext(gen)
    assert chk is not None


@pytest.mark.asyncio
async def test_checkpointer_factory_other(monkeypatch):
    monkeypatch.setattr(settings, "database_url", "mysql://user:pass@localhost/db")
    gen = checkpointer_factory()
    chk = await anext(gen)
    assert chk is not None


@pytest.mark.asyncio
async def test_checkpointer_factory_memory(monkeypatch):
    monkeypatch.setattr(settings, "database_url", "sqlite:///:memory:")
    gen = checkpointer_factory()
    chk = await anext(gen)
    assert chk is not None


@pytest.mark.asyncio
async def test_checkpointer_factory_sqlite_disk(monkeypatch, tmp_path):
    """Cover the AsyncSqliteSaver disk-based branch (lines 44-48)."""
    db_file = tmp_path / "checkpointer_test.db"
    monkeypatch.setattr(settings, "database_url", f"sqlite+aiosqlite:///{db_file}")
    gen = checkpointer_factory()
    chk = await anext(gen)
    assert chk is not None
    try:
        await anext(gen)
    except StopAsyncIteration:
        pass
