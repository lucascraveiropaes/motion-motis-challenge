import json
from collections.abc import AsyncGenerator

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from langgraph.checkpoint.base import BaseCheckpointSaver
from sqlalchemy.orm import Session

from classifier_agent.database import get_db_session_factory
from classifier_agent.graph import GraphContext, build_graph
from classifier_agent.models import (
    StreamRequest,
    TransactionClassifyRequest,
    TransactionClassifyResponse,
    TransactionRecord,
    TransactionResponseItem,
)
from classifier_agent.resources import LLMService, checkpointer_factory, http_client_factory, llm_service_factory
from classifier_agent.services import ClassificationService

router = APIRouter()


@router.post("/transactions/classify", response_model=TransactionClassifyResponse)
def classify_transactions(
    request: TransactionClassifyRequest,
    db: Session = Depends(get_db_session_factory),
) -> TransactionClassifyResponse:
    results = ClassificationService(db).classify_batch(request.descriptions)
    return TransactionClassifyResponse(results=results)


@router.post("/stream/transactions")
async def stream_transactions(
    request: StreamRequest,
    llm_service: LLMService = Depends(llm_service_factory),
    http_client: httpx.AsyncClient = Depends(http_client_factory),
    checkpointer: BaseCheckpointSaver = Depends(checkpointer_factory),
    db: Session = Depends(get_db_session_factory),
) -> StreamingResponse:
    async def event_generator() -> AsyncGenerator[str, None]:
        context = GraphContext(llm_service=llm_service, http_client=http_client)
        graph = build_graph(context, checkpointer=checkpointer)
        final_state: dict = {}

        async for mode, chunk in graph.astream(
            {"description": request.description, "messages": [], "category": ""},
            config={"configurable": {"thread_id": request.thread_id}},
            stream_mode=["custom", "updates"],
        ):
            if mode == "custom":
                yield f"data: {json.dumps(chunk)}\n\n"
            elif mode == "updates":
                final_state.update(chunk.get("classify", {}))

        if category := final_state.get("category"):
            db.add(TransactionRecord(description=request.description, category=category))
            db.commit()

        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")
