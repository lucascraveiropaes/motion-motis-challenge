from datetime import datetime
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class TransactionRecord(Base):
    __tablename__ = "transaction_records"

    id = Column(Integer, primary_key=True, index=True)
    description = Column(String, nullable=False)
    category = Column(String, nullable=False)
    processed_at = Column(DateTime, default=datetime.utcnow)


class ClassificationJob(Base):
    """Tracks async classification batch jobs (Stretch Goal 1)."""

    __tablename__ = "classification_jobs"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(String, unique=True, index=True, nullable=False)
    status = Column(String, default="pending", nullable=False)  # pending | processing | completed
    results: Optional[str] = Column(Text, nullable=True)  # JSON-encoded list when completed
    created_at = Column(DateTime, default=datetime.utcnow)
