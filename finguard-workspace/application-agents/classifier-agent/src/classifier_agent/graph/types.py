from dataclasses import dataclass, field

import httpx

from classifier_agent.graph.messages import StreamMessage
from classifier_agent.resources.checkpointer import Checkpointer
from classifier_agent.resources.llm_service import LLMService


@dataclass
class GraphState:
    thread_id: str
    description: str
    human_decision: str | None = None
    category: str | None = None
    interrupted: bool = False
    draft_id: str | None = None
    events: list[StreamMessage] = field(default_factory=list)


@dataclass
class GraphContext:
    llm_service: LLMService
    http_client: httpx.AsyncClient
    checkpointer: Checkpointer
