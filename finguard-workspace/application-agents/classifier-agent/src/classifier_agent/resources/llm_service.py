from functools import cache

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from classifier_agent.settings import get_settings

_SYSTEM_PROMPT = (
    "Classify the bank transaction description into exactly one of these categories: "
    "Food, Subscription, Shopping, Salary, Uncategorized. "
    "Return only the category name, nothing else."
)


class LLMService:
    def __init__(self, api_key: str, model: str, temperature: int) -> None:
        self.llm = ChatOpenAI(api_key=api_key, model=model, temperature=temperature)

    async def classify(self, description: str) -> str:
        messages = [
            SystemMessage(content=_SYSTEM_PROMPT),
            HumanMessage(content=description),
        ]
        response = await self.llm.ainvoke(messages)
        return str(response.content).strip()


@cache
def llm_service_factory() -> LLMService:
    s = get_settings()
    return LLMService(api_key=s.openai_api_key, model=s.openai_model, temperature=s.openai_temperature)
