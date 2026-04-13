## 1. Project FinGuard
**FinGuard** is an automated financial assistant that processes raw bank transaction descriptions and classifies them into meaningful categories (e.g., "Food", "Subscriptions", "Salary") while detecting potential fraudulent patterns.

The system is divided into:
1.  **Shared Logic (`packages/`)**: A core library for classification rules and data sanitization.
2.  **Service Layer (`application-agents/`)**: A FastAPI-based agent with streaming responses and dependency injection.

---

## 1.1 Technical Architecture

This code challenge evaluates advanced Python skills using:

1. **Dependency Injection (DI)**: FastAPI's `Depends()` pattern with factory functions for all services
   - Database connections via `get_db()` or factory functions
   - HTTP clients (e.g., httpx.AsyncClient) injected per-request
   - Singleton services (LLM, cache) via `@cache` decorator
   - Support for dependency overrides in tests

2. **Streaming Responses (SSE)**: Real-time streaming via `StreamingResponse` with Server-Sent Events
   - Format: `data: {json}\n\n`
   - Message types: `SimpleMessage`, `ChatMessage`, `OrderMessage`, etc.
   - End event: `{type: 'done'}`
   - Integration with `graph.astream()` for LangGraph

3. **Graph-Based Processing**: Integration with LangGraph for stateful, node-based workflows
   - `GraphState` for workflow state
   - `GraphContext` dataclass for passing services to nodes
   - Checkpointers for conversation persistence
   - Support for interrupts (human-in-the-loop)

4. **Service Layer Pattern**: Isolated services injected into the graph
   - LLMService for AI operations
   - Database session/connection
   - HTTP clients for external APIs
   - Elasticsearch clients for search

---

## 2. Candidate Requirements
*   **Python 3.13+**
*   **[uv](https://github.com/astral-sh/uv)** for package management and workspaces.
*   **[just](https://github.com/casey/just)** for task automation.
*   **SQLite/Postgres** for persistence (SQLAlchemy/SQLModel).
*   **LangGraph** for graph-based agent orchestration.
*   **FastAPI** with streaming and dependency injection patterns.

---

## 3. Desired Workspace Structure

The candidate is expected to initialize and build the following structure:
```text
finguard-workspace/
├── pyproject.toml           # Workspace Configuration (uv workspace)
├── justfile                 # Standard automation commands
├── .python-version          # Fixed at 3.13
├── packages/
│   └── transaction-engine/  # Pure business logic
│       ├── pyproject.toml
│       └── src/transaction_engine/classifier.py
└── application-agents/
    └── classifier-agent/    # FastAPI Service with DI
        ├── pyproject.toml
        ├── src/
        │   ├── config/      # TOML-based configurations
        │   └── classifier_agent/
        │       ├── app.py              # FastAPI app with DI
        │       ├── controllers/        # Route handlers
        │       │   └── agent_controller.py  # Stream endpoint
        │       ├── models.py           # Pydantic models
        │       ├── resources/          # Dependency factories
        │       │   ├── __init__.py
        │       │   ├── llm_service.py
        │       │   └── http_client.py
        │       ├── graph/              # LangGraph definition
        │       │   ├── __init__.py
        │       │   ├── state.py        # GraphState
        │       │   ├── nodes.py        # Graph nodes
        │       │   └── agent_graph.py  # CompiledStateGraph
        │       └── services/           # Business services
        │           ├── __init__.py
        │           └── classification_service.py
        └── tests/
            ├── conftest.py
            └── test_classification.py
```

### 3.1 Key Architecture Patterns

The candidate should demonstrate these patterns:
- **Dependency Injection**: Use FastAPI `Depends()` with factory functions in `resources/`
- **GraphContext**: Create a dataclass to pass injected services to LangGraph nodes
- **Stream Endpoint**: Return `StreamingResponse` with `media_type="text/event-stream"`

---

## 4. Automation: The Justfile

The candidate must provide a `justfile` in the root to ensure standard execution:

```just
set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

# Install all workspace dependencies (including dev and prod groups)
install:
    uv sync --all-packages --group dev --group prod

# Run linting and formatting (Ruff)
lint:
    uv run ruff check .
    uv run ruff format . --check

# Type checking with mypy
typecheck:
    uv run mypy .

# Execute tests with coverage report
test:
    uv run pytest application-agents/classifier-agent -vv --cov=classifier_agent --cov=transaction_engine

# Start the agent in development mode
dev:
    uv run fastapi dev application-agents/classifier-agent/src/classifier_agent/app.py --port 8080

# Run with custom port
dev-port port:
    uv run fastapi dev application-agents/classifier-agent/src/classifier_agent/app.py --port {{port}}
```

---

## 5. The Challenge Tasks

### Task 1: Core Engine Implementation
Implement a `classify_transaction(description: str) -> str` function in the `transaction-engine` package.
*   **Rules:** 
    *   Contains "Starbucks" or "McDonalds" -> `Food`
    *   Contains "Netflix" or "Spotify" -> `Subscription`
    *   Contains "Amazon" or "Walmart" -> `Shopping`
    *   Else -> `Uncategorized`

### Task 2: Agent API with Dependency Injection
Create a `POST /transactions/classify` endpoint in the `classifier-agent` that:
1.  Accepts a list of raw transaction strings.
2.  Uses the shared `transaction-engine` to classify them.
3.  Returns a list of structured objects.
4.  **DI Pattern**: Inject database session via `Depends(get_db_session_factory)`

### Task 3: Persistence with Dependency Injection
Integrate a database (SQLAlchemy) with proper DI pattern:
1.  Create a `get_db_session_factory()` function that returns a session generator
2.  Use FastAPI `Depends(get_db_session_factory)` to inject database sessions
3.  Store every classification request and its result for auditing
4.  Support both SQLite (development) and Postgres (production) via config

### Task 4: Stream Endpoint Implementation
Implement a `POST /stream/transactions` endpoint that returns a `StreamingResponse` with Server-Sent Events (SSE):
1.  Return `StreamingResponse` with `media_type="text/event-stream"`
2.  Yield messages in format: `data: {json}\n\n`
3.  Send `{type: 'done'}` when stream completes
4.  Use `graph.astream()` with `stream_mode=["custom", "updates"]`
5.  Inject dependencies: `llm_service`, `http_client`, `db_session` via `Depends()`

### Task 5: Dependency Injection Setup
Set up FastAPI dependency injection with factory functions in `resources/`:
1.  Create factory functions: `llm_service_factory`, `http_client_factory`, `checkpointer_factory`
2.  Use `@cache` decorator for singleton services (like LLMService)
3.  Inject dependencies via FastAPI's `Depends()` in the endpoint
4.  Support dependency overrides in tests via `app.dependency_overrides`

### Task 6: LangGraph Integration
Create a LangGraph-based classification workflow:
1.  Define a `GraphState` dataclass with messages and classification data
2.  Create a `GraphContext` dataclass to hold injected services (llm_service, http_client, etc.)
3.  Build a `StateGraph` with nodes that use services from GraphContext
4.  Compile the graph as `CompiledStateGraph[GraphState, GraphContext]`
5.  Pass services to nodes via GraphContext (not via config)

---

## 6. Validation Suite (The "Black Box" Tests)

Provide these tests to the candidate. They will only pass if the architecture and logic are correct.

### `application-agents/classifier-agent/tests/test_classification.py`
```python
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_classification_flow(client: AsyncClient):
    """Verify that the API correctly classifies a known description."""
    payload = {"descriptions": ["Starbucks Coffee", "Netflix Monthly"]}
    response = await client.post("/transactions/classify", json=payload)
    
    assert response.status_code == 200
    results = response.json()["results"]
    assert results[0]["category"] == "Food"
    assert results[1]["category"] == "Subscription"

@pytest.mark.asyncio
async def test_persistence(client: AsyncClient, db_session):
    """Verify that classified transactions are saved to the database."""
    from classifier_agent.models import TransactionRecord
    
    await client.post("/transactions/classify", json={"descriptions": ["Walmart Store"]})
    
    record = db_session.query(TransactionRecord).first()
    assert record is not None
    assert record.category == "Shopping"

@pytest.mark.asyncio
async def test_stream_endpoint(client: AsyncClient):
    """Verify that the stream endpoint returns SSE format."""
    async with client.stream(
        "POST",
        "/stream/transactions",
        json={"description": "Starbucks Coffee", "thread_id": "test-123"}
    ) as response:
        assert response.status_code == 200
        assert response.headers["content-type"] == "text/event-stream; charset=utf-8"
        
        chunks = []
        async for chunk in response.aiter_lines():
            if chunk.startswith("data: "):
                chunks.append(chunk[6:])
        
        # Should have at least one message + done
        assert len(chunks) >= 2
        import json
        first_msg = json.loads(chunks[0])
        assert first_msg.get("type") == "ai" or "message" in first_msg
        done_msg = json.loads(chunks[-1])
        assert done_msg["type"] == "done"

@pytest.mark.asyncio
async def test_dependency_injection():
    """Verify that dependencies are correctly injected."""
    from classifier_agent.resources import llm_service_factory, http_client_factory
    from classifier_agent.app import app
    
    # Verify factories are callable
    assert callable(llm_service_factory)
    assert callable(http_client_factory)
    
    # Verify app has dependency overrides setup
    assert hasattr(app, "dependency_overrides")

@pytest.mark.asyncio
async def test_graph_context():
    """Verify that GraphContext is properly defined."""
    from classifier_agent.graph.types import GraphContext
    
    # Should have the required service attributes
    assert hasattr(GraphContext, '__dataclass_fields__')
    fields = GraphContext.__dataclass_fields__
    assert 'llm_service' in fields
    assert 'http_client' in fields
```

---

## 7. Evaluation Criteria
1.  **Workspace Integrity:** Did they use `uv add <package> --workspace` correctly?
2.  **Code Coverage:** Does `just test` show > 90% coverage?
3.  **Separation of Concerns:** Is the classification logic strictly kept in `packages/`?
4.  **Configuration:** Did they follow the `config/*.toml` pattern for environment variables?
5.  **Stream Implementation:** Does `/stream/transactions` return SSE format with proper message types?
6.  **Dependency Injection (Database):** Is DB session properly injected via `Depends()`? Not a global singleton.
7.  **Dependency Injection (Services):** Are factory functions in `resources/` properly implemented with `@cache` for singletons and per-request generators?
8.  **Dependency Overrides in Tests:** Can dependencies be overridden via `app.dependency_overrides`?
9.  **LangGraph Integration:** Is GraphState and GraphContext properly defined with services passed via context?

## 8. Senior "Stretch" Goals (Optional)

### Stretch Goal 1: Asynchronous Batch Processor
* Instead of processing immediately, the API should return a `job_id`.
* A background task (using FastAPI's `BackgroundTasks`) should process the transactions and update the database status.

### Stretch Goal 2: Multi-Message Types in Stream
* Implement different message types: `SimpleMessage`, `OrderMessage`, `DraftOrderMessage`, `ChatMessage`
* Use Pydantic models with discriminated union for type-safe message handling
* Handle LangGraph interrupts (human-in-the-loop) in the stream

### Stretch Goal 3: Checkpointer Persistence
* Implement a checkpointer factory that supports SQLite, Postgres, and in-memory backends
* Configure LangGraph to persist conversation state across requests using `thread_id`
* Add ability to resume conversations from saved state
