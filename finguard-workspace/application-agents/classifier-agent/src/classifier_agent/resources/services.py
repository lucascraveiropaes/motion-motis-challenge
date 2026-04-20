import functools


class LLMService:
    """Mock LLM Service class."""

    pass


class HttpClient:
    """Mock HTTP Client class."""

    pass


from langgraph.checkpoint.memory import MemorySaver
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

# If postgres were added, it would be AsyncPostgresSaver from langgraph-checkpoint-postgres
from classifier_agent.config import settings


@functools.cache
def llm_service_factory() -> LLMService:
    """Factory to return a singleton LLMService."""
    return LLMService()


@functools.cache
def http_client_factory() -> HttpClient:
    """Factory to return a singleton HttpClient."""
    return HttpClient()


async def checkpointer_factory():
    """FastAPI Dependency yielding a Checkpointer (Stretch Goal 3)."""
    url = settings.database_url

    if url.startswith("sqlite") or url.startswith("sqlite+aiosqlite"):
        if "memory" in url:
            yield MemorySaver()
        else:
            # LangGraph AsyncSqliteSaver expects standard sqlite URI
            clean_url = url.replace("sqlite+aiosqlite:///", "")
            async with AsyncSqliteSaver.from_conn_string(clean_url) as saver:
                # We need to setup the checkpointer tables if they don't exist
                await saver.setup()
                yield saver
    elif url.startswith("postgresql"):
        # Placeholder for AsyncPostgresSaver
        yield MemorySaver()
    else:
        yield MemorySaver()
