"""Classification API schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    """Batch classification input."""

    descriptions: list[str] = Field(min_length=1)


class ClassifiedTransactionResponse(BaseModel):
    """Classified item returned by the API."""

    description: str
    category: str


class TransactionResponse(BaseModel):
    """Batch classification response."""

    results: list[ClassifiedTransactionResponse]


class StreamTransactionRequest(BaseModel):
    """Stream endpoint input."""

    description: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)
