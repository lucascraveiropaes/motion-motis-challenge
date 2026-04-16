"""Streaming agent controller.

Exposes ``POST /stream/transactions`` which runs the classification graph
and streams intermediate events over Server-Sent Events (SSE). Dependencies
(LLM service, HTTP client, DB session) are injected via FastAPI's
``Depends()`` and handed to the graph through ``GraphContext``.
"""

from __future__ import annotations

import json
from collections.abc import AsyncIterator

import httpx
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from classifier_agent.graph import GraphContext, GraphState, build_agent_graph
from classifier_agent.models import StreamTransactionRequest
from classifier_agent.resources import (
    get_db_session_factory,
    http_client_factory,
    llm_service_factory,
)
from classifier_agent.services.llm_service import LLMService

router = APIRouter(tags=["stream"])


def _sse(payload: dict[str, object]) -> str:
    return f"data: {json.dumps(payload)}\n\n"


async def _stream_graph(
    request: StreamTransactionRequest,
    llm_service: LLMService,
    http_client: httpx.AsyncClient,
    db_session: AsyncSession,
) -> AsyncIterator[str]:
    graph = build_agent_graph()
    context = GraphContext(
        llm_service=llm_service,
        http_client=http_client,
        db_session=db_session,
    )
    initial_state = GraphState(description=request.description)
    config = {"configurable": {"thread_id": request.thread_id or "default"}}

    async for mode, chunk in graph.astream(  # type: ignore[call-overload]
        initial_state,
        config=config,
        context=context,
        stream_mode=["custom", "updates"],
    ):
        if mode == "custom":
            yield _sse(chunk)
        elif mode == "updates":
            # Surface per-node updates so clients can render progress.
            for node_name, node_update in chunk.items():
                yield _sse({"type": "update", "node": node_name, "data": _safe(node_update)})

    yield _sse({"type": "done"})


def _safe(value: object) -> object:
    """Best-effort JSON-safe projection of a node update."""
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


@router.post("/stream/transactions")
async def stream_transactions(
    request: StreamTransactionRequest,
    llm_service: LLMService = Depends(llm_service_factory),
    http_client: httpx.AsyncClient = Depends(http_client_factory),
    db_session: AsyncSession = Depends(get_db_session_factory),
) -> StreamingResponse:
    return StreamingResponse(
        _stream_graph(request, llm_service, http_client, db_session),
        media_type="text/event-stream",
    )
