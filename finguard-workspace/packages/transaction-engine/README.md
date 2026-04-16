# transaction-engine

Pure business logic for classifying raw bank transaction descriptions and
sanitizing noisy input. No framework dependencies so it can be reused by the
`classifier-agent` service, batch jobs, or notebooks.

## Usage

```python
from transaction_engine import classify_transaction

classify_transaction("Starbucks Coffee")  # -> "Food"
classify_transaction("NETFLIX.COM BILL")  # -> "Subscription"
```
