from collections.abc import AsyncIterator

import httpx


async def http_client_factory() -> AsyncIterator[httpx.AsyncClient]:
    async with httpx.AsyncClient(timeout=10.0) as client:
        yield client
