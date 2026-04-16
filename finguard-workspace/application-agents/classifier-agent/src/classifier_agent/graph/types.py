from dataclasses import dataclass

import httpx

from classifier_agent.resources.llm_service import LLMService


@dataclass
class GraphContext:
    llm_service: LLMService
    http_client: httpx.AsyncClient
