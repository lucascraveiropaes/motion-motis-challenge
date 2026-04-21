from transaction_primitives import ClassificationService, Transaction


def test_classify_web_returns_online_purchase():
    service = ClassificationService()
    tx = Transaction(amount=50, merchant="Shop A", channel="web")

    assert service.classify(tx) == "online_purchase"


def test_classify_non_web_returns_mobile_purchase():
    service = ClassificationService()
    tx = Transaction(amount=50, merchant="Shop A", channel="mobile")

    assert service.classify(tx) == "mobile_purchase"


def test_classification_cache_key_includes_channel():
    service = ClassificationService()
    web_tx = Transaction(amount=100, merchant="Shop B", channel="web")
    mobile_tx = Transaction(amount=100, merchant="Shop B", channel="mobile")

    assert service.classify(web_tx) == "online_purchase"
    assert service.classify(mobile_tx) == "mobile_purchase"


def test_is_suspicious_true_when_amount_is_greater_than_threshold():
    service = ClassificationService()
    tx = Transaction(amount=1200, merchant="Shop C", channel="web")

    assert service.is_suspicious(tx) is True


def test_is_suspicious_true_when_amount_equals_threshold():
    service = ClassificationService()
    tx = Transaction(amount=1000, merchant="Shop C", channel="web")

    assert service.is_suspicious(tx) is True


def test_is_suspicious_false_when_below_threshold():
    service = ClassificationService()
    tx = Transaction(amount=999.99, merchant="Shop C", channel="web")

    assert service.is_suspicious(tx) is False
