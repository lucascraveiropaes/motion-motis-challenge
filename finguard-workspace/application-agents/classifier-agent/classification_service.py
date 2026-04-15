"""
ClassificationService: bridges transaction-engine and the API layer.

Responsibilities:
- Call transaction-engine's classify_many()
- Optionally persist results to DB (via injected Session)
- Map domain types → API response models
"""
from sqlalchemy.orm import Session

from transaction_engine.classifier import classify_many, ClassifiedTransaction

from classifier_agent.models import ClassifiedTransactionResponse, ClassifyResponse


class ClassificationService:
    def __init__(self, db: Session) -> None:
        self._db = db

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(self, raw_transactions: list[str]) -> ClassifyResponse:
        classified = classify_many(raw_transactions)
        self._persist(classified)
        return ClassifyResponse.from_results(
            [self._to_response(c) for c in classified]
        )

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _persist(self, results: list[ClassifiedTransaction]) -> None:
        """
        Persist classified transactions to the DB.
        Extend with your ORM model when ready — no-op placeholder for now.
        """
        # Example:
        #   for r in results:
        #       self._db.add(TransactionRecord.from_domain(r))
        # The session is committed / rolled-back by get_db_session_factory.
        pass

    @staticmethod
    def _to_response(ct: ClassifiedTransaction) -> ClassifiedTransactionResponse:
        return ClassifiedTransactionResponse(
            raw=ct.raw,
            category=ct.category,
            merchant=ct.merchant,
            amount=ct.amount,
            confidence=ct.confidence,
        )
