## 🎯 Purpose
This PR implements the **FinGuard** automated financial assistant challenge in its entirety. It provides a full solution for processing raw bank transaction descriptions, classifying them into meaningful categories, and setting up an architecture ready for LangGraph and streaming.

Closes #1 (or relevant issue)

## 🛠️ Implementation Details
This branch consolidates all 6 required tasks into a unified architecture:

1. **Task 1: Core Engine Implementation**: Added a rule-based `classify_transaction` function in the `transaction-engine` package to handle initial transaction categorization ("Food", "Subscription", "Shopping").
2. **Task 2: Agent API with Dependency Injection**: Set up the `POST /transactions/classify` endpoint in `classifier-agent` to accept raw descriptions and use the shared engine.
3. **Task 3: Persistence with Dependency Injection**: Integrated SQLAlchemy via `Depends(get_db_session_factory)` to persist classification records for auditing, keeping the DB session tied to the request lifecycle.
4. **Task 4: Stream Endpoint Implementation**: Added `POST /stream/transactions` using `StreamingResponse` with Server-Sent Events (SSE) to yield JSON objects and a final `{"type": "done"}` event.
5. **Task 5: Dependency Injection Setup**: Implemented dependency factories (`llm_service_factory`, `http_client_factory`) in `resources/` with `@cache` decorators for singleton management.
6. **Task 6: LangGraph Integration**: Defined `GraphState` and `GraphContext` dataclasses to run stateful graph workflows, passing the injected services via context instead of configuration.

**Architectural Changes**:
- Leveraged `uv` workspaces to strictly separate the `transaction-engine` (pure logic) from the `classifier-agent` (FastAPI service layer).
- Followed modern DI patterns (no global singletons for DB sessions/services).

## 🧪 Testing Performed
- [ ] Unit tests passed (specifically `test_classification_flow`, `test_persistence`, `test_stream_endpoint`, `test_dependency_injection`, and `test_graph_context`).
- [ ] Integration tests passed (All endpoints verified via `just test`).
- [ ] Code Coverage is maintained at > 90% for both the agent and the transaction engine.
- [ ] Manual validation (Tested via cURL/HTTP requests to both REST and SSE endpoints).
- [ ] Linting and formatting pass cleanly (`just lint` and `just format`).
- [ ] Type checking passes cleanly (`just typecheck`).

## 📸 Proof of Work (Optional but Recommended)
*(To be added upon completion of the implementation: Screenshots of the passing test suite (`just test` output) and cURL responses for the stream endpoint).*

---

### Evaluation Criteria Checklist
- [ ] **1. Workspace Integrity**: `uv add <package> --workspace` used correctly.
- [ ] **2. Code Coverage**: > 90% via `just test`.
- [ ] **3. Separation of Concerns**: Classification logic is strictly in `packages/`.
- [ ] **4. Configuration**: `.toml` pattern implemented.
- [ ] **5. Stream Implementation**: `/stream/transactions` returns SSE.
- [ ] **6. Dependency Injection (Database)**: DB session properly injected.
- [ ] **7. Dependency Injection (Services)**: Factory functions implemented with `@cache`.
- [ ] **8. Dependency Overrides in Tests**: Handled via `app.dependency_overrides`.
- [ ] **9. LangGraph Integration**: `GraphState` and `GraphContext` properly defined.

### Senior Stretch Goals
- [ ] Stretch Goal 1: Asynchronous Batch Processor
- [ ] Stretch Goal 2: Multi-Message Types in Stream
- [ ] Stretch Goal 3: Checkpointer Persistence
