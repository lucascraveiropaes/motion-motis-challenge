"""Schemas da API de classificacao."""

from __future__ import annotations

from pydantic import BaseModel, Field


class TransactionRequest(BaseModel):
    """Entrada para classificacao em lote."""

    descriptions: list[str] = Field(min_length=1)


class ClassifiedTransactionResponse(BaseModel):
    """Item classificado retornado pela API."""

    description: str
    category: str


class TransactionResponse(BaseModel):
    """Resposta da classificacao em lote."""

    results: list[ClassifiedTransactionResponse]


class StreamTransactionRequest(BaseModel):
    """Entrada do endpoint de stream."""

    description: str = Field(min_length=1)
    thread_id: str = Field(min_length=1)
