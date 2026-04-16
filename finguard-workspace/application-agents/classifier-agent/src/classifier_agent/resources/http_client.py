"""HTTP client factory.

Yields a fresh ``httpx.AsyncClient`` per request so callers always get a
client with a live connection pool and the timeout configured for the
current environment.
"""

from __future__ import annotations

from collections.abc import AsyncIterator

import httpx

from classifier_agent.settings import get_settings


async def http_client_factory() -> AsyncIterator[httpx.AsyncClient]:
    settings = get_settings()
    async with httpx.AsyncClient(timeout=settings.http_timeout_seconds) as client:
        yield client
