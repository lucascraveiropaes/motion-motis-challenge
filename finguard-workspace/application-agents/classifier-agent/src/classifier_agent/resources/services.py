import functools


class LLMService:
    """Mock LLM Service class."""

    pass


class HttpClient:
    """Mock HTTP Client class."""

    pass


class Checkpointer:
    """Mock Checkpointer class for LangGraph persistence (Stretch Goal 3)."""

    pass


@functools.cache
def llm_service_factory() -> LLMService:
    """Factory to return a singleton LLMService."""
    return LLMService()


@functools.cache
def http_client_factory() -> HttpClient:
    """Factory to return a singleton HttpClient."""
    return HttpClient()


@functools.cache
def checkpointer_factory() -> Checkpointer:
    """Factory to return a singleton Checkpointer."""
    return Checkpointer()
