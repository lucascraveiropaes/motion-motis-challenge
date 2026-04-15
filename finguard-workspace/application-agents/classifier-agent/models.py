"""
Pydantic models for classifier-agent API layer.
Kept separate from transaction-engine domain types so the API contract
can evolve independently.
"""
from pydantic import BaseModel, Field
from transaction_engine.classifier import TransactionCategory


# ---------------------------------------------------------------------------
# Request
# ---------------------------------------------------------------------------

class ClassifyRequest(BaseModel):
    transactions: list[str] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Raw transaction strings to classify.",
        examples=[["Uber ride $12.50", "Netflix monthly $15.99", "Salary deposit $3200"]],
    )


# ---------------------------------------------------------------------------
# Response
# ---------------------------------------------------------------------------

class ClassifiedTransactionResponse(BaseModel):
    raw: str
    category: TransactionCategory
    merchant: str | None
    amount: float | None
    confidence: float = Field(..., ge=0.0, le=1.0)


class ClassifyResponse(BaseModel):
    results: list[ClassifiedTransactionResponse]
    total: int

    @classmethod
    def from_results(cls, results: list[ClassifiedTransactionResponse]) -> "ClassifyResponse":
        return cls(results=results, total=len(results))
