"""Database resources: async engine, session maker, and per-request session.

We keep the engine and sessionmaker as cached singletons (expensive to
create, safe to share) while the session itself is request-scoped so each
request commits/rolls-back independently.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from functools import cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

from classifier_agent.models import Base
from classifier_agent.settings import get_settings


@cache
def engine_factory() -> AsyncEngine:
    settings = get_settings()
    return create_async_engine(settings.database_url, future=True)


@cache
def session_maker_factory() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(engine_factory(), expire_on_commit=False, class_=AsyncSession)


async def init_models() -> None:
    """Create tables if they don't exist.

    Used on startup for SQLite-based dev; production relies on Alembic.
    """
    async with engine_factory().begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db_session_factory() -> AsyncIterator[AsyncSession]:
    """Yield a request-scoped AsyncSession bound to the configured engine."""
    session_maker = session_maker_factory()
    async with session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise


def reset_database_cache() -> None:
    """Drop cached engine/sessionmaker. Used between test sessions."""
    engine_factory.cache_clear()
    session_maker_factory.cache_clear()
