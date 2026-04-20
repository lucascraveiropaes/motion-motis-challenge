from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from classifier_agent.config import settings

# Async engine for runtime
engine = create_async_engine(settings.database_url)
SessionLocal = async_sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=AsyncSession)

async def get_db_session_factory():
    db = SessionLocal()
    try:
        yield db
    finally:
        await db.close()


def init_db():
    from classifier_agent.models import Base
    
    # We use a synchronous engine just for creating tables if using sqlite local file
    # Otherwise we'd need async migrations (alembic) or async connection handling
    # For this PoC, we will create a sync engine to create all tables
    sync_url = settings.database_url.replace("+aiosqlite", "")
    sync_engine = create_engine(sync_url)
    Base.metadata.create_all(bind=sync_engine)
