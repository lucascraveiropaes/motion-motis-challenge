# FinGuard Challenge Implementation Plan: Task 4

This plan covers **Task 4: Stream Endpoint Implementation** and natively integrates **Stretch Goal 2: Multi-Message Types in Stream**.

## Goal Description
Task 4 focuses on implementing a highly responsive Server-Sent Events (SSE) streaming endpoint. This endpoint will accept a transaction description and stream back events in real-time as they are "processed" by the system. While the final LangGraph implementation won't be ready until Task 6, we will build the exact API contract, SSE response format, and dependency injections required by the test.

We will also implement **Stretch Goal 2** by designing the stream to explicitly emit multiple types of messages (`status`, `ai`, and `done`).

## Proposed Changes

### 1. Request Models
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/app.py`
- Create a `StreamRequest` Pydantic model with `description` (str) and `thread_id` (str).

### 2. Mocking Services (Bridging to Task 5 & 6)
#### [NEW] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/resources/services.py`
- Create mock `get_llm_service` and `get_http_client` dependencies. These will act as placeholders for Task 5.

### 3. Stream Generator & Stretch Goal 2
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/app.py`
- Create an asynchronous generator `event_stream_generator(request, db, llm, http)` that mimics what `graph.astream()` will eventually do.
- **Stretch Goal 2 Integration:** The generator will yield three distinct message types as JSON:
  1. `{"type": "status", "data": "Connecting to classifier..."}`
  2. `{"type": "ai", "data": {"category": "<category>"}}` (It will call our existing `classify_transaction` using `asyncio.to_thread`).
  3. `{"type": "done"}`

### 4. The SSE Endpoint
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/app.py`
- Add `@app.post("/stream/transactions")`.
- Inject `db_session`, `llm_service`, and `http_client` via `Depends()`.
- Return a `StreamingResponse` wrapping `event_stream_generator`, formatted explicitly as `data: <json>\n\n`.
- Set the `media_type` to `"text/event-stream"`.

### 5. Testing Integration
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/tests/test_classification.py`
- Add the `test_stream_endpoint` provided in the challenge README.

## Verification Plan & Proof of Work

### Automated Tests
1. **Unit Tests**: Run `just test`.
   *Target Proof*: `test_stream_endpoint` passes successfully, validating the `text/event-stream` format and the presence of both the `ai` message type and the `done` message type.
2. **Coverage**: Ensure `test_stream_endpoint` brings the streaming endpoint code coverage up to project standards (>90%).

### Evaluation Criteria Checklist (per README.md)
- [x] **5. Stream Implementation**: `/stream/transactions` returns SSE correctly.
- [x] **Stretch Goal 2**: Multi-Message Types in Stream implemented (yielding `status`, `ai`, and `done`).
