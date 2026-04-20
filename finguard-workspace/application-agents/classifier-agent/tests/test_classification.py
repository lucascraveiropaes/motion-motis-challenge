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
