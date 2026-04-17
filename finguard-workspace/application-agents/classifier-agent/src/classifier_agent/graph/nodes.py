from typing import Literal
from uuid import uuid4

from classifier_agent.graph.messages import ChatMessage, DraftOrderMessage, OrderMessage, SimpleMessage
from classifier_agent.graph.types import GraphContext, GraphState
from classifier_agent.services.classification_service import ClassificationService


async def classify_node(state: GraphState, context: GraphContext) -> GraphState:
    service = ClassificationService()
    category = service.classify(state.description)
    hint = await context.llm_service.classify_hint(state.description)

    state.category = category
    state.events.append(ChatMessage(role="assistant", message=hint))

    if "ORDER" in state.description.upper() and not state.human_decision:
        state.interrupted = True
        state.draft_id = state.draft_id or f"draft-{uuid4().hex[:8]}"
        state.events.append(
            DraftOrderMessage(
                draft_id=state.draft_id,
                message="Human approval required. Resume stream with a decision.",
            )
        )
        state.events.append(SimpleMessage(message="interrupt"))
        return state

    if state.human_decision in {"approved", "rejected"}:
        state.interrupted = False
        order_id = (state.draft_id or f"order-{uuid4().hex[:8]}").replace("draft", "order")
        status: Literal["approved", "rejected"] = "approved" if state.human_decision == "approved" else "rejected"
        state.events.append(OrderMessage(order_id=order_id, status=status, category=category))

    return state
