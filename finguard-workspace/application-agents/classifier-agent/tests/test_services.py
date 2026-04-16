"""Unit tests for the service layer, bypassing FastAPI."""

from __future__ import annotations

import pytest
from classifier_agent.models import TransactionRecord
from classifier_agent.services import ClassificationService, RuleBasedLLMService


@pytest.mark.asyncio
async def test_classification_service_persists_and_returns(async_session_maker) -> None:
    async with async_session_maker() as session:
        service = ClassificationService(llm_service=RuleBasedLLMService(), db_session=session)
        results = await service.classify_and_store(["Spotify Family", "Target Run"])

    assert [r.category for r in results] == ["Subscription", "Shopping"]

    async with async_session_maker() as session:
        rows = (await session.execute(_select_all())).scalars().all()
        assert {r.description for r in rows} == {"Spotify Family", "Target Run"}


def _select_all():
    from sqlalchemy import select

    return select(TransactionRecord)


@pytest.mark.asyncio
async def test_rule_based_llm_service_classifies() -> None:
    svc = RuleBasedLLMService()
    assert await svc.classify("McDonalds") == "Food"
    assert await svc.classify("Mystery Inc") == "Uncategorized"
