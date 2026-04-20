# FinGuard Challenge Implementation Plan: Task 5

This plan covers **Task 5: Dependency Injection Setup**. I will also specifically lay the groundwork for **Stretch Goal 3: Checkpointer Persistence** by preparing the `checkpointer_factory` alongside the required service factories.

## Goal Description
In Task 4, we created basic mock functions (`get_llm_service`, `get_http_client`). Task 5 formalizes these into a robust, scalable Dependency Injection architecture using Python's `functools.cache` to enforce the Singleton pattern. This avoids the anti-pattern of global variables while ensuring that heavy services (like an LLM client or HTTP connection pool) are only instantiated once. 

We will expose these explicitly through `resources/__init__.py` and ensure they pass the test suite's dependency verification logic.

## Proposed Changes

### 1. Refactor Service Factories
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/resources/services.py`
- Create placeholder classes for the services: `LLMService`, `HttpClient`, and `Checkpointer`.
- Create factory functions:
  - `llm_service_factory() -> LLMService`
  - `http_client_factory() -> HttpClient`
  - `checkpointer_factory() -> Checkpointer` **(Stretch Goal 3 Support)**
- Decorate each factory function with `@functools.cache` to ensure they function as Singletons across the FastAPI application.

### 2. Export Resources
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/resources/__init__.py`
- Export the newly created factories, along with our existing `get_db_session_factory`:
```python
from .database import get_db_session_factory
from .services import llm_service_factory, http_client_factory, checkpointer_factory

__all__ = [
    "get_db_session_factory",
    "llm_service_factory",
    "http_client_factory",
    "checkpointer_factory"
]
```

### 3. Update the Endpoint Injections
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/app.py`
- Update the `POST /stream/transactions` endpoint to use the new factory names via FastAPI's `Depends()`:
```python
    llm=Depends(llm_service_factory),
    http=Depends(http_client_factory)
```

### 4. Testing Integration
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/tests/test_classification.py`
- Append the `test_dependency_injection` test block from the challenge README to verify that the factories are callable and that `app.dependency_overrides` is active.

## Verification Plan & Proof of Work

### Automated Tests
1. **Unit Tests**: Run `just test`.
   *Target Proof*: `test_dependency_injection` will pass alongside the existing tests, verifying that the `resources/__init__.py` exposes the correct factory signatures.
2. **Coverage**: Validate that coverage remains strictly >90%.

### Evaluation Criteria Checklist (per README.md)
- [x] **7. Dependency Injection (Services)**: Factory functions implemented with `@cache`.
- [x] **Stretch Goal 3 Support**: `checkpointer_factory` implemented ahead of Task 6.
