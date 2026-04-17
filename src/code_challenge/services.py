"""Servicos de negocio da classificacao."""

from __future__ import annotations

from dataclasses import dataclass

from .graph import ClassifiedTransaction, execute_classification_graph
from .resources import AuditRecord, InMemoryAuditStore


@dataclass(slots=True)
class ClassificationService:
    """Orquestra classificacao e persistencia de auditoria."""

    audit_store: InMemoryAuditStore

    def classify_many(self, descriptions: list[str]) -> list[ClassifiedTransaction]:
        graph_result = execute_classification_graph(descriptions)
        self._save_audit(graph_result.transactions)
        return list(graph_result.transactions)

    def classify_one(self, description: str) -> ClassifiedTransaction:
        return self.classify_many([description])[0]

    def _save_audit(self, transactions: tuple[ClassifiedTransaction, ...]) -> None:
        # A persistencia final deve migrar para DB com sessao injetada.
        for item in transactions:
            self.audit_store.save(AuditRecord(description=item.description, category=item.category))
