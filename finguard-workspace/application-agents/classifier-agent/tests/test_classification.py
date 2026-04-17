import asyncio
import json

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_classification_flow(client: AsyncClient):
    payload = {"descriptions": ["Starbucks Coffee", "Netflix Monthly"]}
    response = await client.post("/transactions/classify", json=payload)

    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["category"] == "Food"
    assert results[1]["category"] == "Subscription"


@pytest.mark.asyncio
async def test_persistence(client: AsyncClient, db_session):
    from classifier_agent.models import TransactionRecord

    await client.post("/transactions/classify", json={"descriptions": ["Walmart Store"]})

    record = db_session.query(TransactionRecord).first()
    assert record is not None
    assert record.category == "Shopping"


@pytest.mark.asyncio
async def test_stream_endpoint(client: AsyncClient):
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
    from classifier_agent.app import app
    from classifier_agent.resources import http_client_factory, llm_service_factory

    assert callable(llm_service_factory)
    assert callable(http_client_factory)
    assert hasattr(app, "dependency_overrides")


@pytest.mark.asyncio
async def test_dependency_override_db_session(client: AsyncClient):
    from classifier_agent.app import app
    from classifier_agent.resources import get_db_session_factory

    class FakeSession:
        def __init__(self) -> None:
            self.added: list[object] = []
            self.commits = 0

        def add(self, record: object) -> None:
            self.added.append(record)

        def commit(self) -> None:
            self.commits += 1

    fake_session = FakeSession()

    def override_db_session():
        yield fake_session

    app.dependency_overrides[get_db_session_factory] = override_db_session
    try:
        response = await client.post(
            "/transactions/classify",
            json={"descriptions": ["Starbucks Coffee", "Netflix Monthly"]},
        )
    finally:
        app.dependency_overrides.pop(get_db_session_factory, None)

    assert response.status_code == 200
    assert fake_session.commits == 2
    assert len(fake_session.added) == 2


@pytest.mark.asyncio
async def test_graph_context():
    from classifier_agent.graph.types import GraphContext

    assert hasattr(GraphContext, "__dataclass_fields__")
    fields = GraphContext.__dataclass_fields__
    assert "llm_service" in fields
    assert "http_client" in fields


@pytest.mark.asyncio
async def test_async_batch_processor_returns_job_id(client: AsyncClient):
    response = await client.post(
        "/transactions/classify/async",
        json={"descriptions": ["Netflix Monthly", "Amazon Market"]},
    )
    assert response.status_code == 200

    payload = response.json()
    assert "job_id" in payload
    assert payload["status"] == "queued"

    job_id = payload["job_id"]
    latest = None
    for _ in range(20):
        latest = await client.get(f"/transactions/classify/jobs/{job_id}")
        assert latest.status_code == 200
        if latest.json()["status"] == "completed":
            break
        await asyncio.sleep(0.01)

    assert latest is not None
    body = latest.json()
    assert body["status"] == "completed"
    assert len(body["results"]) == 2


@pytest.mark.asyncio
async def test_stream_multi_message_and_resume(client: AsyncClient):
    thread_id = "thread-order-1"
    first_chunks = []

    async with client.stream(
        "POST",
        "/stream/transactions",
        json={"description": "Order for Starbucks", "thread_id": thread_id},
    ) as response:
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                first_chunks.append(json.loads(line[6:]))

    types = {chunk.get("type") for chunk in first_chunks}
    assert "chat" in types
    assert "draft_order" in types
    assert any(chunk.get("type") == "done" for chunk in first_chunks)

    second_chunks = []
    async with client.stream(
        "POST",
        "/stream/transactions",
        json={
            "description": "Order for Starbucks",
            "thread_id": thread_id,
            "resume": True,
            "human_decision": "approved",
        },
    ) as response:
        assert response.status_code == 200
        async for line in response.aiter_lines():
            if line.startswith("data: "):
                second_chunks.append(json.loads(line[6:]))

    assert any(chunk.get("type") == "order" for chunk in second_chunks)


@pytest.mark.asyncio
async def test_checkpointer_persistence():
    from classifier_agent.resources import checkpointer_factory

    checkpointer = checkpointer_factory()
    checkpointer.put("thread-xyz", {"state": "saved", "count": 1})
    assert checkpointer.get("thread-xyz") == {"state": "saved", "count": 1}
