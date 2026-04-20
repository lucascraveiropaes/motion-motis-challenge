import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_classification_flow(client: AsyncClient):
    """
    Verify the async batch flow (Stretch Goal 1):
    POST returns 202 + job_id, GET /job_id returns completed results.
    """
    payload = {"descriptions": ["Starbucks Coffee", "Netflix Monthly"]}

    # 1. Enqueue the job
    response = await client.post("/transactions/classify", json=payload)
    assert response.status_code == 202
    data = response.json()
    assert "job_id" in data
    job_id = data["job_id"]

    # 2. Poll for results (background task completes synchronously in ASGI tests)
    result_response = await client.get(f"/transactions/classify/{job_id}")
    assert result_response.status_code == 200
    result_data = result_response.json()
    assert result_data["status"] == "completed"
    results = result_data["results"]
    assert results[0]["category"] == "Food"
    assert results[1]["category"] == "Subscription"


@pytest.mark.asyncio
async def test_classify_job_not_found(client: AsyncClient):
    """Polling a non-existent job_id returns 404."""
    response = await client.get("/transactions/classify/non-existent-job-id")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_persistence(client: AsyncClient, db_session):
    """
    Verify that classified transactions are saved to the database
    after the background job completes.
    """
    from classifier_agent.models import TransactionRecord
    from sqlalchemy import select

    response = await client.post("/transactions/classify", json={"descriptions": ["Walmart Store"]})
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    # Poll until completed (in ASGI tests the background task runs synchronously)
    result_response = await client.get(f"/transactions/classify/{job_id}")
    assert result_response.json()["status"] == "completed"

    result = await db_session.execute(select(TransactionRecord))
    record = result.scalars().first()
    assert record is not None
    assert record.category == "Shopping"


@pytest.mark.asyncio
async def test_stream_endpoint(client: AsyncClient):
    """Verify that the stream endpoint returns SSE format."""
    async with client.stream(
        "POST", "/stream/transactions", json={"description": "Starbucks Coffee", "thread_id": "test-123"}
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"

        chunks = []
        async for chunk in response.aiter_lines():
            if chunk.startswith("data: "):
                chunks.append(chunk[6:])

        assert len(chunks) >= 2
        import json

        first_msg = json.loads(chunks[0])
        assert first_msg.get("type") == "status" or first_msg.get("type") == "ai" or "message" in first_msg
        done_msg = json.loads(chunks[-1])
        assert done_msg["type"] == "done"


@pytest.mark.asyncio
async def test_dependency_injection():
    """Verify that dependencies are correctly injected."""
    from classifier_agent.app import app
    from classifier_agent.resources import checkpointer_factory, http_client_factory, llm_service_factory

    assert callable(llm_service_factory)
    assert callable(http_client_factory)
    assert callable(checkpointer_factory)
    assert hasattr(app, "dependency_overrides")


@pytest.mark.asyncio
async def test_graph_context():
    """Verify that GraphContext is properly defined."""
    from classifier_agent.graph.types import GraphContext

    assert hasattr(GraphContext, "__dataclass_fields__")
    fields = GraphContext.__dataclass_fields__
    assert "llm_service" in fields
    assert "http_client" in fields
