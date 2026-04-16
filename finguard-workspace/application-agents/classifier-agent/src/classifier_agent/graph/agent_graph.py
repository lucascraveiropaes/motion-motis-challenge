"""Compile the classifier StateGraph into a runnable pipeline."""

from __future__ import annotations

from functools import cache
from typing import TYPE_CHECKING

from langgraph.graph import END, START, StateGraph

from classifier_agent.graph.nodes import classify_node, persist_node
from classifier_agent.graph.state import GraphState
from classifier_agent.graph.types import GraphContext
from classifier_agent.resources.checkpointer import checkpointer_factory

if TYPE_CHECKING:
    from langgraph.graph.state import CompiledStateGraph


def _build_uncompiled() -> StateGraph[GraphState, GraphContext, GraphState, GraphState]:
    graph: StateGraph[GraphState, GraphContext, GraphState, GraphState] = StateGraph(
        GraphState, context_schema=GraphContext
    )
    graph.add_node("classify", classify_node)
    graph.add_node("persist", persist_node)
    graph.add_edge(START, "classify")
    graph.add_edge("classify", "persist")
    graph.add_edge("persist", END)
    return graph


@cache
def build_agent_graph() -> CompiledStateGraph[GraphState, GraphContext, GraphState, GraphState]:
    """Compile the graph once per process and memoize it."""
    return _build_uncompiled().compile(checkpointer=checkpointer_factory())
