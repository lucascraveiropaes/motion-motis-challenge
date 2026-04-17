from collections.abc import AsyncIterator

from classifier_agent.graph.nodes import classify_node
from classifier_agent.graph.types import GraphContext, GraphState


class CompiledStateGraph:
    async def astream(
        self,
        state: GraphState,
        *,
        context: GraphContext,
        stream_mode: list[str] | None = None,
    ) -> AsyncIterator[dict]:
        persisted_state = context.checkpointer.get(state.thread_id)
        if persisted_state:
            state.category = persisted_state.get("category")
            state.interrupted = persisted_state.get("interrupted", False)
            state.draft_id = persisted_state.get("draft_id")

        updated_state = await classify_node(state, context)

        for event in updated_state.events:
            yield event.model_dump()

        if stream_mode and "updates" in stream_mode:
            yield {
                "type": "update",
                "description": updated_state.description,
                "category": updated_state.category,
                "interrupted": updated_state.interrupted,
            }

        context.checkpointer.put(
            updated_state.thread_id,
            {
                "description": updated_state.description,
                "category": updated_state.category,
                "interrupted": updated_state.interrupted,
                "draft_id": updated_state.draft_id,
            },
        )


def build_graph() -> CompiledStateGraph:
    return CompiledStateGraph()
