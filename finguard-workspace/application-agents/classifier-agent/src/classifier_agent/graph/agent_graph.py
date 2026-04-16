from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from .nodes import make_classify_node
from .state import GraphState
from .types import GraphContext


def build_graph(
    context: GraphContext,
    checkpointer: BaseCheckpointSaver | None = None,
) -> CompiledStateGraph[GraphState, GraphState]:
    graph: StateGraph[GraphState] = StateGraph(GraphState)
    graph.add_node("classify", make_classify_node(context))
    graph.set_entry_point("classify")
    graph.add_edge("classify", END)
    return graph.compile(checkpointer=checkpointer)
