"""LLM service abstraction.

The protocol keeps controllers and graph nodes decoupled from whichever
backend (rule-based PoC, OpenAI, Anthropic, local Llama, ...) is wired up by
the resource factories. Swapping implementations is a one-line change in
``resources/llm_service.py``.
"""

from __future__ import annotations

from typing import Protocol, runtime_checkable

from transaction_engine import classify_transaction


@runtime_checkable
class LLMService(Protocol):
    """Structural type for anything that can classify a description."""

    async def classify(self, description: str) -> str: ...


class RuleBasedLLMService:
    """First-round PoC implementation backed by the rule-based engine."""

    def __init__(self) -> None:
        self._classify = classify_transaction

    async def classify(self, description: str) -> str:
        return self._classify(description)
