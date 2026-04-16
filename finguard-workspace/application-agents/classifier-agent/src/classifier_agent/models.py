"""SQLAlchemy and Pydantic models for the classifier agent."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Literal

from pydantic import BaseModel, Field
from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Declarative base for all SQLAlchemy models in this service."""


class TransactionRecord(Base):
    __tablename__ = "transaction_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC), nullable=False)


class TransactionRequest(BaseModel):
    descriptions: list[str] = Field(..., examples=[["Starbucks Coffee", "Netflix Monthly"]], min_length=1)


class TransactionResponseItem(BaseModel):
    description: str
    category: str


class TransactionResponse(BaseModel):
    results: list[TransactionResponseItem]


class StreamTransactionRequest(BaseModel):
    description: str
    thread_id: str | None = None


class SimpleMessage(BaseModel):
    type: Literal["ai"] = "ai"
    message: str


class ChatMessage(BaseModel):
    type: Literal["chat"] = "chat"
    role: str
    message: str


class OrderMessage(BaseModel):
    type: Literal["order"] = "order"
    description: str
    category: str


class DoneMessage(BaseModel):
    type: Literal["done"] = "done"
