from transaction_engine.classifier import classify_transaction


class ClassificationService:
    def classify(self, description: str) -> str:
        return classify_transaction(description)
