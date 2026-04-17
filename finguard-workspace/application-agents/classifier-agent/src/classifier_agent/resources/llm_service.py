from functools import cache


class LLMService:
    async def classify_hint(self, description: str) -> str:
        return f"Classifying transaction: {description}"


@cache
def llm_service_factory() -> LLMService:
    return LLMService()
