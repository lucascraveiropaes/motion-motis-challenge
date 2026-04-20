from dataclasses import dataclass
from typing import Optional, TypedDict

from sqlalchemy.ext.asyncio import AsyncSession

from classifier_agent.resources.services import HttpClient, LLMService


class GraphState(TypedDict):
    """The state of the classification graph."""
    description: str
    category: Optional[str]


@dataclass
class GraphContext:
    """The context containing injected dependencies for the graph."""
    llm_service: LLMService
    http_client: HttpClient
    db_session: AsyncSession
