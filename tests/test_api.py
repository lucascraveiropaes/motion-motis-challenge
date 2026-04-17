import json

from fastapi.testclient import TestClient

from code_challenge.app import create_app
from code_challenge.resources import InMemoryAuditStore, get_classification_service
from code_challenge.services import ClassificationService


def _build_client_with_overrides() -> tuple[TestClient, InMemoryAuditStore]:
    app = create_app()
    audit_store = InMemoryAuditStore()
    service = ClassificationService(audit_store=audit_store)
    app.dependency_overrides[get_classification_service] = lambda: service
    return TestClient(app), audit_store


def test_healthcheck() -> None:
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_classification_endpoint_and_audit() -> None:
    client, audit_store = _build_client_with_overrides()

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
    assert [record.category for record in audit_store.list_records()] == ["Food", "Uncategorized"]


def test_stream_transactions_endpoint_sse() -> None:
    client, audit_store = _build_client_with_overrides()

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
    assert [record.category for record in audit_store.list_records()] == ["Subscription"]
