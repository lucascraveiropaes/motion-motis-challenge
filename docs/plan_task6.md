# FinGuard Challenge Implementation Plan: Task 6

This plan covers the final milestone, **Task 6: LangGraph Integration**, while fully satisfying the requirements of **Stretch Goal 3: Checkpointer Persistence**.

## Goal Description
We will replace our mock streaming generator from Task 4 with a true, stateful LangGraph workflow. The graph will manage state via `GraphState` and receive dependencies explicitly via `GraphContext` (bypassing the global config anti-pattern). To fulfill Stretch Goal 3, we will dynamically instantiate the correct asynchronous `langgraph-checkpoint` saver based on our database configuration, enabling persistent memory across threads.

## Proposed Changes

### 1. Workspace Dependencies
- Install the required LangGraph packages for the `classifier-agent` workspace: `langgraph`, `langchain-core`, and `langgraph-checkpoint-sqlite`. (Since we are using `ext.asyncio` for SQLite, we will utilize `langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver`).

### 2. Graph State & Context Definitions
#### [NEW] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/graph/types.py`
- Define `GraphState` (as a `TypedDict` or `dataclass`) containing fields like `description`, `category`, and `messages`.
- Define `GraphContext` (as a `dataclass`) containing `llm_service`, `http_client`, and `db_session`. This satisfies the core architectural constraint.

### 3. Checkpointer Factory (Stretch Goal 3)
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/resources/services.py`
- Upgrade the mocked `checkpointer_factory`.
- It will inspect the application config (`database_url`) and dynamically yield an `AsyncSqliteSaver`, a hypothetical `AsyncPostgresSaver`, or fallback to a `MemorySaver`.

### 4. StateGraph Workflow
#### [NEW] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/graph/workflow.py`
- Build the `StateGraph` using `GraphState` and `GraphContext`.
- Create a `classify_node(state: GraphState, config: RunnableConfig)` that extracts the context, utilizes the classification engine to determine the category, and dispatches custom updates to simulate the events from Stretch Goal 2.
- Compile the graph using the checkpointing saver from our factory.

### 5. Update the SSE Endpoint
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/app.py`
- Refactor `event_stream_generator` to invoke `graph.astream(...)`.
- The endpoint will wrap the injected dependencies (`llm`, `http`, `db`) into the `GraphContext` and provide it alongside the `checkpointer`.
- Stream the exact `data: <json>\n\n` formats that satisfy the SSE validation test.

### 6. Testing Integration
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/tests/test_classification.py`
- Append the `test_graph_context` block to verify `GraphContext` contains the required properties (`llm_service` and `http_client`).

## Verification Plan & Proof of Work

### Automated Tests
1. **Unit Tests**: Run `just test`.
   *Target Proof*: `test_graph_context` will pass. Critically, `test_stream_endpoint` must *continue* to pass despite replacing the mock generator with the fully compiled LangGraph engine.
2. **Coverage**: Validate that the new `graph/` package brings/maintains coverage strictly >90%.

### Evaluation Criteria Checklist (per README.md)
- [ ] **9. LangGraph Integration**: `GraphState` and `GraphContext` properly defined.
- [ ] **Stretch Goal 3**: Checkpointer Persistence natively handles session state using `thread_id`.
