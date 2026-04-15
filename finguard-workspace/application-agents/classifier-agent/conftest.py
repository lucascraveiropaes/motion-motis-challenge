"""
Pytest fixtures for classifier-agent tests.
Overrides get_db_session_factory with an in-memory SQLite session.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from classifier_agent.app import app
from classifier_agent.resources.db import Base, get_db_session_factory


# ---------------------------------------------------------------------------
# In-memory test DB
# ---------------------------------------------------------------------------

_TEST_ENGINE = create_engine(
    "sqlite:///:memory:",
    connect_args={"check_same_thread": False},
)
_TestSessionFactory = sessionmaker(bind=_TEST_ENGINE, autocommit=False, autoflush=False)


def _override_db() -> Session:
    db = _TestSessionFactory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    Base.metadata.create_all(bind=_TEST_ENGINE)
    yield
    Base.metadata.drop_all(bind=_TEST_ENGINE)


@pytest.fixture()
def client() -> TestClient:
    app.dependency_overrides[get_db_session_factory] = _override_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()
