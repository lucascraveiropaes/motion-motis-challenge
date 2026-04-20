from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from classifier_agent.config import settings

engine = create_engine(settings.database_url)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db_session_factory():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from classifier_agent.models import Base

    Base.metadata.create_all(bind=engine)
