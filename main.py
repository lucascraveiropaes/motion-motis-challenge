import uvicorn
from transaction_engine.classifier import get_classifier, TransactionClassifier

_classifier: TransactionClassifier = get_classifier()


def classify_transaction(description: str) -> str:
    return _classifier.classify_transaction(description)


def main():
    uvicorn.run(
        "classifier_agent.app:app",
        host="0.0.0.0",
        port=8080,
        reload=True,
    )


if __name__ == "__main__":
    main()
