from datetime import UTC, datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TransactionRecord(Base):
    __tablename__ = "transaction_records"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    description: Mapped[str] = mapped_column(String, nullable=False)
    category: Mapped[str] = mapped_column(String, nullable=False)
    processed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(UTC))
