from collections.abc import AsyncGenerator

import httpx
from langgraph.checkpoint.memory import MemorySaver


async def http_client_factory() -> AsyncGenerator[httpx.AsyncClient, None]:
    async with httpx.AsyncClient() as client:
        yield client


def checkpointer_factory() -> MemorySaver:
    return MemorySaver()
