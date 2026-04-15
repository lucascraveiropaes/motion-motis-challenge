"""
Tests for POST /transactions/classify
"""
import pytest
from fastapi.testclient import TestClient


ENDPOINT = "/transactions/classify"


def test_classify_known_transactions(client: TestClient):
    response = client.post(ENDPOINT, json={
        "transactions": [
            "Uber ride $12.50",
            "Netflix monthly $15.99",
            "Salary deposit $3200",
        ]
    })
    assert response.status_code == 200
    body = response.json()
    assert body["total"] == 3

    categories = {r["raw"]: r["category"] for r in body["results"]}
    assert categories["Uber ride $12.50"] == "transport"
    assert categories["Netflix monthly $15.99"] == "entertainment"
    assert categories["Salary deposit $3200"] == "income"


def test_classify_unknown_transaction(client: TestClient):
    response = client.post(ENDPOINT, json={"transactions": ["xyzzy payment 999"]})
    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["category"] == "unknown"
    assert result["confidence"] < 0.5


def test_classify_returns_amount(client: TestClient):
    response = client.post(ENDPOINT, json={"transactions": ["Starbucks $6.75"]})
    assert response.status_code == 200
    result = response.json()["results"][0]
    assert result["amount"] == 6.75


def test_empty_transactions_rejected(client: TestClient):
    response = client.post(ENDPOINT, json={"transactions": []})
    assert response.status_code == 422    # Pydantic min_length=1


def test_missing_body_rejected(client: TestClient):
    response = client.post(ENDPOINT, json={})
    assert response.status_code == 422
