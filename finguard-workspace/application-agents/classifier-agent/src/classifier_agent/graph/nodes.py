"""Graph nodes.

Each node receives ``(state, runtime)`` where ``runtime.context`` holds the
injected :class:`GraphContext`. Using ``get_stream_writer`` inside the
classifier node lets us push custom SSE chunks out of the stream without
giving up LangGraph's default update/state streaming.
"""

from __future__ import annotations

from typing import Any

from langgraph.config import get_stream_writer
from langgraph.runtime import Runtime

from classifier_agent.graph.state import GraphState
from classifier_agent.graph.types import GraphContext
from classifier_agent.models import TransactionRecord


async def classify_node(state: GraphState, runtime: Runtime[GraphContext]) -> dict[str, Any]:
    """Classify the current description and emit streaming events."""
    context = runtime.context
    description = state.description
    category = await context.llm_service.classify(description)

    writer = get_stream_writer()
    writer({"type": "ai", "message": f"Classified '{description}' as {category}"})
    writer({"type": "order", "description": description, "category": category})

    return {
        "category": category,
        "messages": state.messages + [{"role": "ai", "content": category}],
    }


async def persist_node(state: GraphState, runtime: Runtime[GraphContext]) -> dict[str, Any]:
    """Persist the classification when a DB session is available."""
    context = runtime.context
    if context.db_session is not None and state.category is not None:
        context.db_session.add(TransactionRecord(description=state.description, category=state.category))
        await context.db_session.commit()
    return {}
