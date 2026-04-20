# FinGuard Challenge Implementation Plan: Task 3

This plan covers **Task 3: Persistence with Dependency Injection**.

## Goal Description
Task 3 focuses on formalizing our database integration using the Dependency Injection pattern and making the application environment-aware. While we already use `Depends(get_db_session_factory)` and save records, we currently have hardcoded SQLite strings in `app.py`. We need to extract this into a proper `resources` module, introduce configuration management via `.toml` files (to support both SQLite and Postgres dynamically), and write the corresponding test.

## Proposed Changes

### 1. Configuration Management (`.toml` Pattern)
#### [NEW] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/config.py`
- Create a configuration class using `pydantic_settings.BaseSettings`.
- It will read from a `config.toml` file (or environment variables) to determine the `DATABASE_URL`.
- Default to `sqlite:///./classifier.db` for local dev, but allow injection of a `postgresql://` string for production.

#### [NEW] `finguard-workspace/application-agents/classifier-agent/config.toml`
- Provide a default `config.toml` with `database_url = "sqlite:///./classifier.db"`.

### 2. Database Refactoring
#### [NEW] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/resources/database.py`
- Move the `create_engine`, `SessionLocal`, and `get_db_session_factory()` logic out of `app.py` into this dedicated resource module.
- The engine will be initialized using the `DATABASE_URL` from the configuration module.

#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/app.py`
- Remove the hardcoded database connection setup.
- Import `get_db_session_factory` from the new `resources.database` module.

### 3. Testing Integration
#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/tests/conftest.py`
- Add a `db_session` pytest fixture that spins up a test SQLite database (`sqlite:///:memory:` or similar test DB).
- Override the FastAPI dependency: `app.dependency_overrides[get_db_session_factory] = override_get_db`.

#### [MODIFY] `finguard-workspace/application-agents/classifier-agent/tests/test_classification.py`
- Add the `test_persistence` test from the README.

## Verification Plan & Proof of Work

All commands should be executed from the **workspace root directory** (`finguard-workspace/`).

### Automated Tests
1. **Unit Tests**: Ran `just test`.
   *Proof*: Both `test_classification_flow` and `test_persistence` pass successfully!
2. **Lint & Format**: Ran `just lint` and `just format`.
   *Proof*: 100% clean formatting.

```text
application-agents/classifier-agent/tests/test_classification.py::test_persistence PASSED
======================== 6 passed, 3 warnings in 0.04s =========================
```

### Evaluation Criteria Checklist (per README.md)
*Note: Criteria already met in Tasks 1 & 2 are excluded.*
- [x] **4. Configuration**: `.toml` pattern implemented via `pydantic-settings` (`TomlConfigSettingsSource`).
- [x] **8. Dependency Overrides in Tests**: Handled via `app.dependency_overrides` for the database session in `conftest.py`.
