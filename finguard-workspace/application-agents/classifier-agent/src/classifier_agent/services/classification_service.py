"""Orchestration layer coordinating the LLM service and the DB session."""

from __future__ import annotations

from collections.abc import Iterable

from sqlalchemy.ext.asyncio import AsyncSession

from classifier_agent.models import TransactionRecord, TransactionResponseItem
from classifier_agent.services.llm_service import LLMService


class ClassificationService:
    """Classify transactions and persist the audit record in one place.

    Using a service layer keeps the controller thin and lets us share the
    same logic between the REST endpoint and the LangGraph node without
    duplicating persistence code.
    """

    def __init__(self, llm_service: LLMService, db_session: AsyncSession) -> None:
        self._llm = llm_service
        self._db = db_session

    async def classify_and_store(self, descriptions: Iterable[str]) -> list[TransactionResponseItem]:
        results: list[TransactionResponseItem] = []
        for description in descriptions:
            category = await self._llm.classify(description)
            self._db.add(TransactionRecord(description=description, category=category))
            results.append(TransactionResponseItem(description=description, category=category))
        await self._db.commit()
        return results
