from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from .settings import get_settings


def _build_url() -> str:
    s = get_settings()
    return f"postgresql://{s.db_user}:{s.db_password}@{s.db_host}:{s.db_port}/{s.db_name}"


engine = create_engine(_build_url())
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session_factory() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    from .models import Base
    Base.metadata.create_all(bind=engine)
