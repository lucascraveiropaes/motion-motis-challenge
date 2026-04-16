from sqlalchemy.orm import Session

from transaction_engine.classifier import classify_transaction

from classifier_agent.models import TransactionRecord, TransactionResponseItem


class ClassificationService:
    def __init__(self, db: Session) -> None:
        self.db = db

    def classify_batch(self, descriptions: list[str]) -> list[TransactionResponseItem]:
        results = []
        for description in descriptions:
            category = classify_transaction(description)
            self.db.add(TransactionRecord(description=description, category=category))
            results.append(TransactionResponseItem(description=description, category=category))
        self.db.commit()
        return results
