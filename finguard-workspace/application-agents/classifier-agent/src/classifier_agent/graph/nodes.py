from langchain_core.messages import AIMessage
from langgraph.config import get_stream_writer

from .state import GraphState
from .types import GraphContext


def make_classify_node(context: GraphContext):
    async def classify_node(state: GraphState) -> dict:
        write = get_stream_writer()

        write({"type": "ai", "message": f"Classifying: {state.description}"})

        category = await context.llm_service.classify(state.description)

        write({"type": "ai", "message": f"Category: {category}"})

        return {
            "category": category,
            "messages": [AIMessage(content=f"Classified '{state.description}' as '{category}'")],
        }

    return classify_node
