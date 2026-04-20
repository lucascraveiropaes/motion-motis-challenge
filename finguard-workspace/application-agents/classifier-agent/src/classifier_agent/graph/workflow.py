import asyncio

from langgraph.graph import END, START, StateGraph
from transaction_engine.classifier import classify_transaction

from classifier_agent.graph.types import GraphContext, GraphState


async def classify_node(state: GraphState, _context: GraphContext):
    """
    Node that runs the classification using the transaction engine.
    (It receives the GraphContext explicitly instead of config).
    """
    # 1. Perform classification (simulating an async AI call that uses context.llm_service if we had one)
    category = await asyncio.to_thread(classify_transaction, state["description"])

    # 2. Return the state update
    return {"category": category}


def get_compiled_graph(context: GraphContext, checkpointer=None):
    """
    Compile the StateGraph for the given request.
    We pass the context to the nodes using closures/partials to avoid config dicts.
    """
    workflow = StateGraph(GraphState)

    # Wrap the node to inject the context directly
    async def classify_node_wrapper(state: GraphState):
        return await classify_node(state, context)

    classify_node_wrapper.__name__ = "classify"  # Keep node name friendly

    workflow.add_node("classify", classify_node_wrapper)
    workflow.add_edge(START, "classify")
    workflow.add_edge("classify", END)

    return workflow.compile(checkpointer=checkpointer)
