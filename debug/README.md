# Debug Tests

This folder contains a standalone debug module and tests for the FinGuard
transaction classification primitives.

## Files

- `transaction_primitives.py`: exercise implementation
- `test_transaction_primitives.py`: pytest test suite

## Run tests

From the repository root:

```bash
pytest debug/test_transaction_primitives.py
```

Or run from inside `debug/`:

```bash
cd debug
pytest test_transaction_primitives.py
```

## Current expected result

With the current implementation in `transaction_primitives.py`, two tests fail:

- cache key does not include `channel` in `classify`
- threshold check in `is_suspicious` uses `>` instead of `>=`

After fixing those bugs, all tests should pass.
