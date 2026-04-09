## 1. Project FinGuard
**FinGuard** is an automated financial assistant that processes raw bank transaction descriptions and classifies them into meaningful categories (e.g., "Food", "Subscriptions", "Salary") while detecting potential fraudulent patterns.

The system is divided into:
1.  **Shared Logic (`packages/`)**: A core library for classification rules and data sanitization.
2.  **Service Layer (`application-agents/`)**: A FastAPI-based agent that receives transactions and persists classified results.

---

## 2. Candidate Requirements
*   **Python 3.13+**
*   **[uv](https://github.com/astral-sh/uv)** for package management and workspaces.
*   **[just](https://github.com/casey/just)** for task automation.
*   **SQLite/Postgres** for persistence (SQLAlchemy/SQLModel).

---

## 3. Desired Workspace Structure

The candidate is expected to initialize and build the following structure:
```text
finguard-workspace/
├── pyproject.toml           # Workspace Configuration
├── justfile                 # Standard automation commands
├── .python-version          # Fixed at 3.13
├── packages/
│   └── transaction-engine/  # Pure business logic
│       ├── pyproject.toml
│       └── src/transaction_engine/classifier.py
└── application-agents/
    └── classifier-agent/    # FastAPI Service
        ├── pyproject.toml
        ├── src/
        │   ├── config/      # TOML-based configurations
        │   └── classifier_agent/
        │       ├── app.py
        │       └── models.py
        └── tests/           # Test suite (to be provided)
            ├── conftest.py
            └── test_classification.py
```

---

## 4. Automation: The Justfile
The candidate must provide a `justfile` in the root to ensure standard execution:

```just
set windows-shell := ["powershell.exe", "-NoProfile", "-Command"]

# Install all workspace dependencies
install:
    uv sync --all-packages

# Run linting and formatting (Ruff)
lint:
    uv run ruff check .
    uv run ruff format . --check

# Execute tests with coverage report
test:
    uv run pytest application-agents/classifier-agent -vv --cov=classifier_agent --cov=transaction_engine

# Start the agent in development mode
dev:
    uv run fastapi dev application-agents/classifier-agent/src/classifier_agent/app.py --port 8080
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

### Task 2: Agent API
Create a `POST /transactions/classify` endpoint in the `classifier-agent` that:
1.  Accepts a list of raw transaction strings.
2.  Uses the shared `transaction-engine` to classify them.
3.  Returns a list of structured objects.

### Task 3: Persistence
Integrate a database (SQLAlchemy) to store every classification request and its result for auditing purposes.

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
```

---

## 7. Evaluation Criteria
1.  **Workspace Integrity:** Did they use `uv add <package> --workspace` correctly?
2.  **Code Coverage:** Does `just test` show > 90% coverage?
3.  **Separation of Concerns:** Is the classification logic strictly kept in `packages/`?
4.  **Configuration:** Did they follow the `config/*.toml` pattern for environment variables?

## 8. Senior "Stretch" Goal (Optional)
Ask the candidate to implement an **Asynchronous Batch Processor**:
*   Instead of processing immediately, the API should return a `job_id`.
*   A background task (using FastAPI's `BackgroundTasks`) should process the transactions and update the database status.
