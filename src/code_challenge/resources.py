"""Dependencias e recursos injetaveis da API."""

from __future__ import annotations

from collections.abc import Generator
from dataclasses import dataclass
from functools import lru_cache


@dataclass(frozen=True, slots=True)
class AuditRecord:
    """Registro de auditoria para classificacoes realizadas."""

    description: str
    category: str


class InMemoryAuditStore:
    """Armazena auditoria em memoria para PoC e testes."""

    def __init__(self) -> None:
        self._records: list[AuditRecord] = []

    def save(self, record: AuditRecord) -> None:
        self._records.append(record)

    def list_records(self) -> list[AuditRecord]:
        return list(self._records)


@lru_cache(maxsize=1)
def audit_store_factory() -> InMemoryAuditStore:
    """Retorna store singleton para facilitar override em testes."""
    return InMemoryAuditStore()


def get_db_session_factory() -> Generator[None, None, None]:
    """Placeholder de sessao de banco via DI.

    Em producao, este provider deve abrir sessao SQLAlchemy, realizar yield
    e fechar a conexao no bloco finally.
    """
    yield None
