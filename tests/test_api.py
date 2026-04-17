import json

from fastapi.testclient import TestClient

from code_challenge.app import create_app


def test_healthcheck() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_classification_endpoint_and_audit() -> None:
    client = TestClient(create_app())

    response = client.post(
        "/transactions/classify",
        json={"descriptions": ["Starbucks Coffee", "Pagamento avulso"]},
    )

    assert response.status_code == 200
    assert response.json() == {
        "results": [
            {"description": "Starbucks Coffee", "category": "Food"},
            {"description": "Pagamento avulso", "category": "Uncategorized"},
        ]
    }


def test_stream_transactions_endpoint_sse() -> None:
    client = TestClient(create_app())

    with client.stream(
        "POST",
        "/stream/transactions",
        json={"description": "Netflix Monthly", "thread_id": "thread-1"},
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("text/event-stream")

        lines = [line for line in response.iter_lines() if line.startswith("data: ")]
        messages = [json.loads(line[6:]) for line in lines]

    assert messages[0]["type"] == "ai"
    assert messages[1]["type"] == "classification"
    assert messages[1]["category"] == "Subscription"
    assert messages[2]["type"] == "done"
