# FinGuard Challenge Implementation Plan: Task 2

This plan covers **Task 2: Agent API with Dependency Injection**.

## Goal Description
The `POST /transactions/classify` endpoint is already mostly scaffolded in `classifier-agent/src/classifier_agent/app.py`. For Task 2, we need to ensure this endpoint properly handles the classification requests via the shared `transaction-engine`, correctly leverages FastAPI's Dependency Injection (`Depends`) for the database session, and passes the validation tests provided in the challenge instructions.

## Proposed Changes

### `classifier-agent` Package

#### [NEW] `finguard-workspace/application-agents/classifier-agent/tests/conftest.py`
- Create a pytest `conftest.py` file to provide the necessary fixtures for testing the FastAPI application asynchronously.
- Provide an `AsyncClient` fixture connected to the FastAPI `app` using `httpx`.

#### [NEW] `finguard-workspace/application-agents/classifier-agent/tests/test_classification.py`
- Create the main test file and copy over the `test_classification_flow` test from the project README.
- This test will verify that a `POST` request to `/transactions/classify` with a list of descriptions correctly returns structured JSON with the proper categories.

#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/app.py`
- Review the existing `classify_transactions_endpoint`. It already uses `Depends(get_db)` and calls the `classify_transaction` engine. We will ensure the implementation matches the exact expectations of `test_classification_flow`.
- Rename `get_db` to `get_db_session_factory` to strictly match the terminology used in Task 2 & 3 of the challenge description.

## Verification Plan & Proof of Work

All commands should be executed from the **workspace root directory** (`finguard-workspace/`).

### Automated Tests
1. **Unit Tests**: Run `just test`.
   *Target Proof*: The newly added `test_classification_flow` test should pass successfully.
2. **Lint & Format**: Run `just lint`.
   *Target Proof*: No new styling or formatting errors introduced.

### Implementation Status Checklist (per DEVELOPMENT_GUIDELINES.md)
- [ ] **Integration tests passed**: `test_classification_flow` verifies the FastAPI endpoint directly.

### Evaluation Criteria Checklist (per README.md)
*Note: Criteria already met in Task 1 are excluded from this focus list.*
- [ ] **2. Code Coverage**: Ensure coverage remains > 90% when integrating the API.
- [ ] **6. Dependency Injection (Database)**: Verified that DB session is properly injected via `Depends()` into the endpoint (not accessed globally).
