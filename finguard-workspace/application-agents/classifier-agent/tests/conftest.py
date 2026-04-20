import pytest_asyncio
from classifier_agent.app import app
from httpx import ASGITransport, AsyncClient


@pytest_asyncio.fixture(scope="session")
async def client():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
