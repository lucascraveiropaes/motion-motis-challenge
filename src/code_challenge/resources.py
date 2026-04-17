"""Injectable API dependencies and resources."""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from functools import lru_cache
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .services import ClassificationService


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """Audit record for completed classifications."""

    description: str
    category: str


class InMemoryAuditStore:
    """In-memory audit storage for PoC and tests."""

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def save(self, record: AuditRecord) -> None:
        self._records.append(record)

    def list_records(self) -> list[AuditRecord]:
        return list(self._records)


@lru_cache(maxsize=1)
def audit_store_factory() -> InMemoryAuditStore:
    """Return singleton store to ease overriding in tests."""
    return InMemoryAuditStore()


def get_db_session_factory() -> Generator[None, None, None]:
    """Database session placeholder via DI.

    In production, this provider should open a SQLAlchemy session, yield,
    and close the connection in a finally block.
    """
    yield None


def get_classification_service() -> ClassificationService:
    """Service provider to ease overriding in tests."""
    from .services import ClassificationService

    return ClassificationService(audit_store=audit_store_factory())
