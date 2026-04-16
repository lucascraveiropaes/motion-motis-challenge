"""LLM service factory. Cached so we reuse a single instance per process."""

from __future__ import annotations

from functools import cache

from classifier_agent.services.llm_service import LLMService, RuleBasedLLMService
from classifier_agent.settings import get_settings


@cache
def llm_service_factory() -> LLMService:
    """Return the singleton LLM service configured for the current env.

    For now the only backend is the rule-based engine from
    ``transaction-engine``. Additional backends (OpenAI, Anthropic, ...) can
    be wired here based on ``settings.llm_backend`` without touching callers.
    """
    settings = get_settings()
    if settings.llm_backend == "rules":
        return RuleBasedLLMService()
    # Fallback keeps the service functional even if config is stale.
    return RuleBasedLLMService()
