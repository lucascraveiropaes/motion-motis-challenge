import pytest


@pytest.mark.asyncio
class TestListTransactions:
    async def test_list_empty(self, client, auth_header):
        response = await client.get("/transactions", headers=auth_header)
        assert response.status_code == 200
        assert response.json() == []

    async def test_list_with_transactions(self, client, auth_header):
        await client.post("/transactions", json={"description": "Starbucks Coffee"}, headers=auth_header)
        await client.post("/transactions", json={"description": "Netflix Monthly"}, headers=auth_header)

        response = await client.get("/transactions", headers=auth_header)
        assert response.status_code == 200
        assert len(response.json()) == 2

    async def test_list_unauthorized(self, client):
        response = await client.get("/transactions")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestGetTransaction:
    async def test_get_existing(self, client, auth_header):
        create_response = await client.post("/transactions", json={"description": "Starbucks Coffee"}, headers=auth_header)
        transaction_id = create_response.json()["id"]

        response = await client.get(f"/transactions/{transaction_id}", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["description"] == "Starbucks Coffee"
        assert response.json()["category"] == "Food"

    async def test_get_not_found(self, client, auth_header):
        response = await client.get("/transactions/999", headers=auth_header)
        assert response.status_code == 404
        assert response.json()["detail"] == "Transaction not found"

    async def test_get_unauthorized(self, client):
        response = await client.get("/transactions/1")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestCreateTransaction:
    async def test_create_food(self, client, auth_header):
        response = await client.post("/transactions", json={"description": "McDonalds Burger"}, headers=auth_header)
        assert response.status_code == 200
        assert response.json()["description"] == "McDonalds Burger"
        assert response.json()["category"] == "Food"

    async def test_create_subscription(self, client, auth_header):
        response = await client.post("/transactions", json={"description": "Spotify Premium"}, headers=auth_header)
        assert response.status_code == 200
        assert response.json()["category"] == "Subscription"

    async def test_create_shopping(self, client, auth_header):
        response = await client.post("/transactions", json={"description": "Amazon Purchase"}, headers=auth_header)
        assert response.status_code == 200
        assert response.json()["category"] == "Shopping"

    async def test_create_uncategorized(self, client, auth_header):
        response = await client.post("/transactions", json={"description": "Random Store"}, headers=auth_header)
        assert response.status_code == 200
        assert response.json()["category"] == "Uncategorized"

    async def test_create_unauthorized(self, client):
        response = await client.post("/transactions", json={"description": "Test"})
        assert response.status_code == 401


@pytest.mark.asyncio
class TestUpdateTransaction:
    async def test_update_description(self, client, auth_header):
        create_response = await client.post("/transactions", json={"description": "Starbucks Coffee"}, headers=auth_header)
        transaction_id = create_response.json()["id"]

        response = await client.put(
            f"/transactions/{transaction_id}",
            json={"description": "Walmart Shopping"},
            headers=auth_header,
        )
        assert response.status_code == 200
        assert response.json()["description"] == "Walmart Shopping"
        assert response.json()["category"] == "Shopping"

    async def test_update_reclassifies(self, client, auth_header):
        create_response = await client.post("/transactions", json={"description": "Starbucks Coffee"}, headers=auth_header)
        transaction_id = create_response.json()["id"]
        assert create_response.json()["category"] == "Food"

        response = await client.put(
            f"/transactions/{transaction_id}",
            json={"description": "Netflix Subscription"},
            headers=auth_header,
        )
        assert response.json()["category"] == "Subscription"

    async def test_update_not_found(self, client, auth_header):
        response = await client.put("/transactions/999", json={"description": "Test"}, headers=auth_header)
        assert response.status_code == 404
        assert response.json()["detail"] == "Transaction not found"

    async def test_update_unauthorized(self, client):
        response = await client.put("/transactions/1", json={"description": "Test"})
        assert response.status_code == 401


@pytest.mark.asyncio
class TestDeleteTransaction:
    async def test_delete_existing(self, client, auth_header):
        create_response = await client.post("/transactions", json={"description": "Starbucks Coffee"}, headers=auth_header)
        transaction_id = create_response.json()["id"]

        response = await client.delete(f"/transactions/{transaction_id}", headers=auth_header)
        assert response.status_code == 200
        assert response.json()["message"] == "Transaction deleted"

        get_response = await client.get(f"/transactions/{transaction_id}", headers=auth_header)
        assert get_response.status_code == 404

    async def test_delete_not_found(self, client, auth_header):
        response = await client.delete("/transactions/999", headers=auth_header)
        assert response.status_code == 404
        assert response.json()["detail"] == "Transaction not found"

    async def test_delete_unauthorized(self, client):
        response = await client.delete("/transactions/1")
        assert response.status_code == 401


@pytest.mark.asyncio
class TestRoot:
    async def test_root(self, client):
        response = await client.get("/")
        assert response.status_code == 200
        assert "message" in response.json()


@pytest.mark.asyncio
class TestAuthentication:
    async def test_invalid_credentials(self, client):
        import base64
        credentials = base64.b64encode(b"admin:wrongpassword").decode("utf-8")
        response = await client.get("/transactions", headers={"Authorization": f"Basic {credentials}"})
        assert response.status_code == 401

    async def test_invalid_scheme(self, client):
        response = await client.get("/transactions", headers={"Authorization": "Bearer token"})
        assert response.status_code == 401

    async def test_missing_header(self, client):
        response = await client.get("/transactions")
        assert response.status_code == 401
