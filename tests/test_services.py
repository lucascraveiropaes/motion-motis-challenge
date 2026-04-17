from code_challenge.resources import InMemoryAuditStore
from code_challenge.services import ClassificationService


def test_service_classify_many_and_audit() -> None:
    store = InMemoryAuditStore()
    service = ClassificationService(audit_store=store)

    results = service.classify_many(["Amazon Marketplace", "Pagamento manual"])

    assert [item.category for item in results] == ["Shopping", "Uncategorized"]
    assert [record.category for record in store.list_records()] == ["Shopping", "Uncategorized"]


def test_service_classify_one() -> None:
    store = InMemoryAuditStore()
    service = ClassificationService(audit_store=store)

    result = service.classify_one("Spotify Premium")

    assert result.category == "Subscription"
    assert len(store.list_records()) == 1
