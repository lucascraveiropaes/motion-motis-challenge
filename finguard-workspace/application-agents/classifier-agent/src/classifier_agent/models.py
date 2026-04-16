from datetime import datetime, timezone

from pydantic import BaseModel
from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import declarative_base

Base = declarative_base()


# --- SQLAlchemy ORM models ---

class TransactionRecord(Base):
    __tablename__ = "transaction_records"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    processed_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))


# --- Pydantic schemas ---

class TransactionResponseItem(BaseModel):
    description: str
    category: str


class TransactionClassifyRequest(BaseModel):
    descriptions: list[str]


class TransactionClassifyResponse(BaseModel):
    results: list[TransactionResponseItem]


class StreamRequest(BaseModel):
    description: str
    thread_id: str = "default"
