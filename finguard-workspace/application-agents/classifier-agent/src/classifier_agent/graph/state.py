"""Graph state shared between nodes."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class GraphState:
    """Mutable state flowing through the classification graph."""

    description: str = ""
    category: str | None = None
    messages: list[dict[str, str]] = field(default_factory=list)
