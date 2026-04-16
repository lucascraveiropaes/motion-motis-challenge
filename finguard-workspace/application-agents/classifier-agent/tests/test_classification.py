import json

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_classification_flow(client: AsyncClient):
    """Verify that the API correctly classifies a known description."""
    payload = {"descriptions": ["Starbucks Coffee", "Netflix Monthly"]}
    response = await client.post("/transactions/classify", json=payload)

    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["category"] == "Food"
    assert results[1]["category"] == "Subscription"


@pytest.mark.asyncio
async def test_persistence(client: AsyncClient, db_session):
    """Verify that classified transactions are saved to the database."""
    from classifier_agent.models import TransactionRecord

    await client.post("/transactions/classify", json={"descriptions": ["Walmart Store"]})

    record = db_session.query(TransactionRecord).first()
    assert record is not None
    assert record.category == "Shopping"


@pytest.mark.asyncio
async def test_stream_endpoint(client: AsyncClient):
    """Verify that the stream endpoint returns SSE format."""
    async with client.stream(
        "POST",
        "/stream/transactions",
        json={"description": "Starbucks Coffee", "thread_id": "test-123"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        chunks = []
        async for chunk in response.aiter_lines():
            if chunk.startswith("data: "):
                chunks.append(chunk[6:])

        assert len(chunks) >= 2
        first_msg = json.loads(chunks[0])
        assert first_msg.get("type") == "ai" or "message" in first_msg
        done_msg = json.loads(chunks[-1])
        assert done_msg["type"] == "done"


@pytest.mark.asyncio
async def test_dependency_injection():
    """Verify that dependencies are correctly injected."""
    from classifier_agent.resources import http_client_factory, llm_service_factory

    assert callable(llm_service_factory)
    assert callable(http_client_factory)

    from classifier_agent.app import app
    assert hasattr(app, "dependency_overrides")


@pytest.mark.asyncio
async def test_graph_context():
    """Verify that GraphContext is properly defined."""
    from classifier_agent.graph.types import GraphContext

    assert hasattr(GraphContext, "__dataclass_fields__")
    fields = GraphContext.__dataclass_fields__
    assert "llm_service" in fields
    assert "http_client" in fields
