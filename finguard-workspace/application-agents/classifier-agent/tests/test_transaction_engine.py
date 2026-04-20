from transaction_engine.classifier import classify_transaction

def test_classify_transaction_food():
    assert classify_transaction("Starbucks Coffee") == "Food"
    assert classify_transaction("McDonalds NYC") == "Food"

def test_classify_transaction_subscription():
    assert classify_transaction("Netflix Monthly") == "Subscription"
    assert classify_transaction("Spotify Premium") == "Subscription"

def test_classify_transaction_shopping():
    assert classify_transaction("Amazon.com") == "Shopping"
    assert classify_transaction("Walmart Store") == "Shopping"

def test_classify_transaction_uncategorized():
    assert classify_transaction("Random Bakery") == "Uncategorized"
