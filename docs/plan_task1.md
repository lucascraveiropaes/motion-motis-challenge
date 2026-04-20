# FinGuard Challenge Implementation Plan: Task 1

This plan covers **Task 1: Core Engine Implementation**. We will focus only on this task to ensure we make incremental progress.

## Goal Description
Implement a simple rule-based PoC version of `classify_transaction(description: str) -> str` in the shared `transaction-engine` package. This function will evaluate transaction descriptions and return a category ("Food", "Subscription", "Shopping", or "Uncategorized").

## Proposed Changes

### `transaction-engine` Package

#### [NEW] `finguard-workspace/packages/transaction-engine/src/transaction_engine/classifier.py`
- Implement `classify_transaction(description: str) -> str`.
- The logic will be a simple case-insensitive substring match:
  - Contains "Starbucks" or "McDonalds" -> `Food`
  - Contains "Netflix" or "Spotify" -> `Subscription`
  - Contains "Amazon" or "Walmart" -> `Shopping`
  - Anything else -> `Uncategorized`

#### [MODIFY] `finguard-workspace/packages/transaction-engine/src/transaction_engine/__init__.py`
- Expose the `classify_transaction` function so it can be imported by the `classifier-agent` as `from transaction_engine.classifier import classify_transaction`.
- Remove the existing placeholder `hello()` function.

## Verification Plan & Proof of Work

All commands were executed from the **workspace root directory** (`finguard-workspace/`).

### Automated Tests
1. **Lint & Format**: Ran `just lint` from `finguard-workspace/`. This executes Ruff across all packages.
   *Proof: `Found 0 errors.` and `5 files reformatted, 2 files left unchanged.`*
2. **Type Checking**: Ran `just typecheck` from `finguard-workspace/`. This runs mypy to enforce static typing.
   *Proof: `Success: no issues found in 8 source files`*
3. **Unit Tests & Coverage**: Ran `just test` from `finguard-workspace/`. This triggers pytest on `application-agents/classifier-agent` while measuring coverage for both the agent and `transaction_engine`.
   *Proof: Coverage output for `transaction_engine` is 100%: 11/11 statements.*

```text
================================ tests coverage ================================
_______________ coverage: platform darwin, python 3.13.5-final-0 _______________

Name                                                               Stmts   Miss  Cover
--------------------------------------------------------------------------------------
packages/transaction-engine/src/transaction_engine/__init__.py         2      0   100%
packages/transaction-engine/src/transaction_engine/classifier.py       9      0   100%
--------------------------------------------------------------------------------------
TOTAL                                                                 11      0   100%
============================== 4 passed in 0.02s ===============================
```

### Implementation Status Checklist (per DEVELOPMENT_GUIDELINES.md)
*Note: Only the tests applicable to Task 1 are listed.*
- [x] **Unit tests passed**: Verified via `just test`. Added `test_transaction_engine.py` to ensure categories are correctly identified.
- [x] **Manual validation**: Tested implicitly via the unit tests proving string matching behaves correctly.

### Evaluation Criteria Checklist (per README.md)
*Note: Only criteria relevant to Task 1 are listed.*
- [x] **1. Workspace Integrity**: `transaction-engine` properly packaged within the `uv` workspace using `hatchling` as the build backend.
- [x] **2. Code Coverage**: 100% coverage achieved via `just test`.
- [x] **3. Separation of Concerns**: Classification logic is strictly kept inside `packages/transaction-engine/`.
