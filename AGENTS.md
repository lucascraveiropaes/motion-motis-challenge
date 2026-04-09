# FinGuard Workspace

## Workspace Location
- **Important**: All development commands run inside `finguard-workspace/`, not the repo root
- The root directory contains project metadata; the actual project lives in `finguard-workspace/`

## Dev Commands (run in `finguard-workspace/`)

```bash
cd finguard-workspace
just install   # Install dependencies (uv sync --all-packages)
just lint      # Run ruff check + format
just test      # Run pytest with coverage
just dev       # Start FastAPI dev server on port 8080
```

## Architecture

- `packages/transaction-engine/` - Shared classification logic with SQLite persistence (`categories.db`)
- `application-agents/classifier-agent/` - FastAPI service with its own SQLite DB (`classifier.db`)

## Key Entry Points
- `finguard-workspace/application-agents/classifier-agent/src/classifier_agent/app.py` - FastAPI app with `/transactions/classify` endpoint
- `finguard-workspace/packages/transaction-engine/src/transaction_engine/classifier.py` - Core `classify_transaction()` function

## Dependencies
- `transaction-engine` imports in `classifier-agent` use package name directly (e.g., `from transaction_engine.classifier import ...`)
