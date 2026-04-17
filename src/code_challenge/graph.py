"""Classification execution via a simple graph."""

from __future__ import annotations

from dataclasses import dataclass, field

from .classifier import classify_transaction


@dataclass(frozen=True, slots=True)
class ClassifiedTransaction:
    """Represents a classified transaction during the flow."""

    description: str
    category: str


@dataclass(frozen=True, slots=True)
class GraphExecutionResult:
    """Consolidated result of graph execution."""

    ordered_nodes: tuple[str, ...]
    edges: tuple[tuple[str, str], ...]
    transactions: tuple[ClassifiedTransaction, ...]


@dataclass(slots=True)
class TransactionGraph:
    """Directed graph to orchestrate the classification pipeline."""

    _adjacency: dict[str, list[str]] = field(default_factory=dict)
    _ordered_nodes: list[str] = field(default_factory=list)

    def add_node(self, node: str) -> None:
        if node in self._adjacency:
            return
        self._adjacency[node] = []
        self._ordered_nodes.append(node)

    def add_edge(self, source: str, target: str) -> None:
        self.add_node(source)
        self.add_node(target)
        if target not in self._adjacency[source]:
            self._adjacency[source].append(target)

    def edges(self) -> tuple[tuple[str, str], ...]:
        return tuple((source, target) for source, targets in self._adjacency.items() for target in targets)

    def ordered_nodes(self) -> tuple[str, ...]:
        return tuple(self._ordered_nodes)


def execute_classification_graph(descriptions: list[str]) -> GraphExecutionResult:
    """Run the classification flow and return the graph result.

    Note: database persistence is not wired up yet. In production,
    a DI-injected session would be passed here to persist audit data.
    """
    graph = TransactionGraph()
    graph.add_node("input")
    graph.add_node("classify")
    graph.add_node("output")
    graph.add_edge("input", "classify")
    graph.add_edge("classify", "output")

    classified_transactions = tuple(
        ClassifiedTransaction(description=description, category=classify_transaction(description))
        for description in descriptions
    )

    return GraphExecutionResult(
        ordered_nodes=graph.ordered_nodes(),
        edges=graph.edges(),
        transactions=classified_transactions,
    )
