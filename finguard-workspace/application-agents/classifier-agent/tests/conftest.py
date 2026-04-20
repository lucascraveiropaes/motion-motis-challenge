import classifier_agent.resources.database as db_module
import pytest_asyncio
from classifier_agent.app import app
from classifier_agent.models import Base
from classifier_agent.resources.database import get_db_session_factory
from classifier_agent.resources.services import checkpointer_factory
from httpx import ASGITransport, AsyncClient
from langgraph.checkpoint.memory import MemorySaver
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

# Create a test database in memory
TEST_DATABASE_URL = "sqlite+aiosqlite:///file:testdb?mode=memory&cache=shared&uri=true"
test_engine = create_async_engine(TEST_DATABASE_URL)
TestingSessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=test_engine, class_=AsyncSession)

# --- Patch the module-level SessionLocal so background tasks also use the test DB ---
db_module.SessionLocal = TestingSessionLocal


async def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        await db.close()


async def override_checkpointer():
    """Use in-memory saver for tests — avoids SQLite file handles."""
    yield MemorySaver()


# Apply dependency overrides
app.dependency_overrides[get_db_session_factory] = override_get_db
app.dependency_overrides[checkpointer_factory] = override_checkpointer


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """Create and drop all tables (including ClassificationJob) for each test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def db_session():
    """Fixture to provide a test database session for direct querying in tests."""
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        await db.close()


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
