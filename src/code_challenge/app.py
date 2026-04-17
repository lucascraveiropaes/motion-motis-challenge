"""Aplicacao FastAPI para classificacao de transacoes."""

from __future__ import annotations

import json
from collections.abc import AsyncGenerator

from fastapi import Depends, FastAPI
from fastapi.responses import StreamingResponse

from .graph import execute_classification_graph
from .resources import AuditRecord, InMemoryAuditStore, audit_store_factory, get_db_session_factory
from .schemas import (
    ClassifiedTransactionResponse,
    StreamTransactionRequest,
    TransactionRequest,
    TransactionResponse,
)


def create_app() -> FastAPI:
    """Cria app com rotas e dependencias injetaveis."""
    app = FastAPI(title="Code Challenge API", version="0.1.0")

    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.post("/transactions/classify", response_model=TransactionResponse)
    async def classify_transactions(
        request: TransactionRequest,
        audit_store: InMemoryAuditStore = Depends(audit_store_factory),
        _: None = Depends(get_db_session_factory),
    ) -> TransactionResponse:
        graph_result = execute_classification_graph(request.descriptions)

        results = [
            ClassifiedTransactionResponse(description=item.description, category=item.category)
            for item in graph_result.transactions
        ]

        # A auditoria em memoria mantem rastreabilidade sem acoplar banco agora.
        for item in results:
            audit_store.save(AuditRecord(description=item.description, category=item.category))

        return TransactionResponse(results=results)

    @app.post("/stream/transactions")
    async def stream_transactions(
        request: StreamTransactionRequest,
        _: None = Depends(get_db_session_factory),
    ) -> StreamingResponse:
        async def event_stream() -> AsyncGenerator[str, None]:
            category = execute_classification_graph([request.description]).transactions[0].category
            yield f"data: {json.dumps({'type': 'ai', 'message': 'Classificacao iniciada'})}\n\n"
            payload = {
                "type": "classification",
                "thread_id": request.thread_id,
                "description": request.description,
                "category": category,
            }
            yield f"data: {json.dumps(payload)}\n\n"
            yield f"data: {json.dumps({'type': 'done'})}\n\n"

        return StreamingResponse(event_stream(), media_type="text/event-stream")

    return app


app = create_app()
