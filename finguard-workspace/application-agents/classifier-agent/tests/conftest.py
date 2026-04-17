import os
import sys
from pathlib import Path

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

PROJECT_SRC = Path(__file__).resolve().parents[1] / "src"
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))


@pytest.fixture
def anyio_backend() -> str:
    return "asyncio"


@pytest.fixture(autouse=True)
def use_test_db(tmp_path: Path) -> None:
    db_file = tmp_path / "test-classifier.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_file}"

    from classifier_agent import resources

    resources.get_session_maker.cache_clear()
    resources.get_engine.cache_clear()
    resources.get_settings.cache_clear()
    resources.checkpointer_factory.cache_clear()

    yield

    # Ensure pooled sqlite connections are explicitly closed between tests.
    try:
        engine = resources.get_engine()
    except Exception:
        engine = None

    if engine is not None:
        engine.dispose()

    resources.get_session_maker.cache_clear()
    resources.get_engine.cache_clear()
    resources.get_settings.cache_clear()
    resources.checkpointer_factory.cache_clear()


@pytest_asyncio.fixture
async def client():
    from classifier_agent.app import app

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture
def db_session():
    from classifier_agent.resources import get_session_maker

    session = get_session_maker()()
    try:
        yield session
    finally:
        session.close()
