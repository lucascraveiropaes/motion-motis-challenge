import json
from collections.abc import AsyncIterator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from classifier_agent.graph import build_graph
from classifier_agent.graph.types import GraphContext, GraphState
from classifier_agent.resources import (
    checkpointer_factory,
    get_db_session_factory,
    http_client_factory,
    llm_service_factory,
)

router = APIRouter()


class StreamRequest(BaseModel):
    description: str
    thread_id: str
    resume: bool = False
    human_decision: str | None = None


async def _event_stream(request: StreamRequest, context: GraphContext) -> AsyncIterator[str]:
    graph = build_graph()

    async for payload in graph.astream(
        GraphState(
            thread_id=request.thread_id,
            description=request.description,
            human_decision=request.human_decision if request.resume else None,
        ),
        context=context,
        stream_mode=["custom", "updates"],
    ):
        yield f"data: {json.dumps(payload)}\n\n"

    yield 'data: {"type": "done"}\n\n'


@router.post("/stream/transactions")
async def stream_transactions(
    request: StreamRequest,
    db_session: Session = Depends(get_db_session_factory),
    http_client=Depends(http_client_factory),
):
    _ = db_session
    context = GraphContext(
        llm_service=llm_service_factory(),
        http_client=http_client,
        checkpointer=checkpointer_factory(),
    )
    return StreamingResponse(_event_stream(request, context), media_type="text/event-stream")
