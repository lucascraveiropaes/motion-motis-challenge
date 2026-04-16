# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**FinGuard** is an automated financial assistant that classifies bank transaction descriptions (e.g., "Starbucks" → `Food`, "Netflix" → `Subscription`) and detects fraudulent patterns. It is a code challenge evaluating FastAPI DI patterns, LangGraph integration, and streaming SSE responses.

## Commands

Install all workspace dependencies:
```bash
just install
# expands to: uv sync --all-packages
```

Lint and format (Ruff):
```bash
just lint
```

Run tests with coverage:
```bash
just test
# expands to: uv run pytest --cov
```

Run the dev server on port 8080:
```bash
just dev
# expands to: uv run fastapi dev application-agents/classifier-agent/src/classifier_agent/app.py --port 8080
```

Run Alembic migrations (from the classifier-agent directory):
```bash
cd application-agents/classifier-agent && uv run alembic upgrade head
```

Add a dependency to a specific workspace member:
```bash
uv add <package> --package classifier-agent
uv add <package> --package transaction-engine
```

## Workspace Structure

This is a `uv` workspace. The root `pyproject.toml` declares members via `[tool.uv.workspace]`:

- **`packages/transaction-engine`** — pure business logic library (no FastAPI, no DB). Contains `classify_transaction(description: str) -> str` in `src/transaction_engine/classifier.py`. This is the only place classification rules may live.
- **`application-agents/classifier-agent`** — FastAPI service that imports from `transaction-engine` and exposes HTTP endpoints.

## Architecture Patterns

The challenge requires these specific patterns — do not simplify them away:

### 1. Dependency Injection via FastAPI `Depends()`
All services (DB session, LLM, HTTP client) must be injected through factory functions in `application-agents/classifier-agent/src/classifier_agent/resources/`. Use `@cache` for singleton services (LLM, HTTP client) and a generator function for per-request DB sessions.

```python
# resources/llm_service.py
@cache
def llm_service_factory() -> LLMService: ...

# app.py
@app.post("/transactions/classify")
async def classify(llm: LLMService = Depends(llm_service_factory), db = Depends(get_db)):
```

Tests must be able to override dependencies via `app.dependency_overrides`.

### 2. Streaming SSE via `StreamingResponse`
The `POST /stream/transactions` endpoint must return `StreamingResponse(media_type="text/event-stream")` yielding lines in the format `data: {json}\n\n`. The final message must be `{"type": "done"}`. Integrate with `graph.astream(stream_mode=["custom", "updates"])`.

### 3. LangGraph Integration
Define a `GraphState` dataclass and a `GraphContext` dataclass in `src/classifier_agent/graph/`. `GraphContext` holds injected services (llm_service, http_client) and is passed to nodes — not via LangGraph's config dict.

```
graph/
  state.py        # GraphState dataclass
  nodes.py        # node functions receiving GraphContext
  agent_graph.py  # CompiledStateGraph[GraphState, GraphContext]
  types.py        # GraphContext dataclass (must have llm_service, http_client fields)
```

### 4. Configuration
Environment-specific settings live in `src/config/*.toml` files (not `.env` files). Use `pydantic-settings` to load them.

## Database

- SQLite for development (`sqlite:///./classifier.db`), Postgres for production.
- Alembic migrations live in `application-agents/classifier-agent/src/alembic/`.
- `alembic.ini` is at `application-agents/classifier-agent/alembic.ini` (run Alembic from that directory).
- The `TransactionRecord` model (`models.py`) stores every classification for auditing.

## Target Directory Structure

The expected final layout for `classifier-agent`:
```
src/classifier_agent/
├── app.py
├── models.py
├── controllers/
│   └── agent_controller.py   # stream endpoint
├── resources/
│   ├── __init__.py
│   ├── llm_service.py
│   └── http_client.py
├── graph/
│   ├── __init__.py
│   ├── state.py
│   ├── nodes.py
│   ├── agent_graph.py
│   └── types.py              # GraphContext
└── services/
    └── classification_service.py
```

## Validation Tests

The acceptance tests from the README must pass. They live (or will live) at `application-agents/classifier-agent/tests/test_classification.py` and test:
- `test_classification_flow` — POST `/transactions/classify` returns correct categories
- `test_persistence` — classified transactions are stored in DB
- `test_stream_endpoint` — `/stream/transactions` returns SSE with `done` event
- `test_dependency_injection` — `llm_service_factory` and `http_client_factory` are callable; app has `dependency_overrides`
- `test_graph_context` — `GraphContext` has `llm_service` and `http_client` dataclass fields
