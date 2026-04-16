"""Checkpointer factory for LangGraph.

Returns an in-memory checkpointer by default so the stream endpoint works
without external infrastructure. Swap ``settings.checkpointer_backend`` to
``"sqlite"`` to persist conversation state across restarts.
"""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from langgraph.checkpoint.memory import MemorySaver

from classifier_agent.settings import get_settings

if TYPE_CHECKING:
    from langgraph.checkpoint.base import BaseCheckpointSaver


@cache
def checkpointer_factory() -> BaseCheckpointSaver:
    settings = get_settings()
    if settings.checkpointer_backend == "sqlite":
        try:
            from langgraph.checkpoint.sqlite import SqliteSaver

            cm = SqliteSaver.from_conn_string(settings.checkpointer_path)
            return cm.__enter__()
        except ImportError:
            # Fall back to memory if the optional dep is missing at runtime.
            return MemorySaver()
    return MemorySaver()
