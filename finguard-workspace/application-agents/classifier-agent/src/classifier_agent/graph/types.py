"""Graph context: services injected into graph nodes.

Passing services via ``GraphContext`` instead of a global or the graph
``config`` keeps nodes trivially testable — swap the dataclass fields with
fakes/mocks and you're done.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import httpx
    from sqlalchemy.ext.asyncio import AsyncSession

    from classifier_agent.services.llm_service import LLMService


@dataclass
class GraphContext:
    """Services available to every node in the classification graph."""

    llm_service: LLMService
    http_client: httpx.AsyncClient
    db_session: AsyncSession | None = None
    extras: dict[str, Any] | None = None
