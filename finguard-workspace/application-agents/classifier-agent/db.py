"""
Database session DI factory.

Usage in route handlers:
    db: Session = Depends(get_db_session_factory)
"""
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, DeclarativeBase

# ---------------------------------------------------------------------------
# Engine & session factory — replace URL with config/env var in production
# ---------------------------------------------------------------------------

_DATABASE_URL = "sqlite:///./finguard.db"   # swap for postgres in prod

_engine = create_engine(
    _DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite-only guard
    echo=False,
)

_SessionFactory = sessionmaker(bind=_engine, autocommit=False, autoflush=False)


# ---------------------------------------------------------------------------
# Base for ORM models (import this in your ORM model files)
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    pass


# ---------------------------------------------------------------------------
# FastAPI dependency
# ---------------------------------------------------------------------------

def get_db_session_factory() -> Generator[Session, None, None]:
    """
    Yields a SQLAlchemy Session for the duration of a single request,
    then rolls back on error and always closes the session.

    Inject via:
        db: Session = Depends(get_db_session_factory)
    """
    db = _SessionFactory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
