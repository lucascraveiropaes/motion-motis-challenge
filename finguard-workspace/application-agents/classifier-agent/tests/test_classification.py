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
