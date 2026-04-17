"""Rotas HTTP da aplicacao."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse

from .resources import get_classification_service, get_db_session_factory
from .schemas import (
    ClassifiedTransactionResponse,
    StreamTransactionRequest,
    TransactionRequest,
    TransactionResponse,
)
from .services import ClassificationService

router = APIRouter()


@router.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@router.post("/transactions/classify", response_model=TransactionResponse)
async def classify_transactions(
    request: TransactionRequest,
    service: ClassificationService = Depends(get_classification_service),
    _: None = Depends(get_db_session_factory),
) -> TransactionResponse:
    results = [
        ClassifiedTransactionResponse(description=item.description, category=item.category)
        for item in service.classify_many(request.descriptions)
    ]
    return TransactionResponse(results=results)


@router.post("/stream/transactions")
async def stream_transactions(
    request: StreamTransactionRequest,
    service: ClassificationService = Depends(get_classification_service),
    _: None = Depends(get_db_session_factory),
) -> StreamingResponse:
    async def event_stream() -> AsyncGenerator[str, None]:
        classified = service.classify_one(request.description)
        yield f"data: {json.dumps({'type': 'ai', 'message': 'Classificacao iniciada'})}\n\n"
        payload = {
            "type": "classification",
            "thread_id": request.thread_id,
            "description": classified.description,
            "category": classified.category,
        }
        yield f"data: {json.dumps(payload)}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")
