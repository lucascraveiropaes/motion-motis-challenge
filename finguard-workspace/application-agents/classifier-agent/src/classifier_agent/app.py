from typing import List

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field

# Import from the workspace package
from transaction_engine.classifier import classify_transaction

from classifier_agent.models import TransactionRecord
from classifier_agent.resources.database import get_db_session_factory, init_db

# Initialize database tables
init_db()

app = FastAPI()


# Pydantic models for request/response
class TransactionRequest(BaseModel):
    descriptions: List[str] = Field(..., examples=["Starbucks Coffee", "Netflix Monthly"])


class TransactionResponseItem(BaseModel):
    description: str
    category: str


class TransactionResponse(BaseModel):
    results: List[TransactionResponseItem]


class StreamRequest(BaseModel):
    description: str = Field(..., examples=["Starbucks Coffee"])
    thread_id: str = Field(..., examples=["test-123"])


import asyncio

from sqlalchemy.ext.asyncio import AsyncSession


@app.post("/transactions/classify", response_model=TransactionResponse)
async def classify_transactions_endpoint(
    request: TransactionRequest, db: AsyncSession = Depends(get_db_session_factory)
):
    """
    Classifies a list of transaction descriptions and stores them in the database.
    Processes the batch concurrently using asyncio.gather.
    """
    # 1. Run classifications concurrently in threads (since the core engine is synchronous)
    tasks = [asyncio.to_thread(classify_transaction, desc) for desc in request.descriptions]
    categories = await asyncio.gather(*tasks)

    # 2. Prepare database records and response items
    db_records = []
    results = []

    for desc, category in zip(request.descriptions, categories):
        db_records.append(TransactionRecord(description=desc, category=category))
        results.append(TransactionResponseItem(description=desc, category=category))

    # 3. Asynchronously persist all records in a single batch
    db.add_all(db_records)
    await db.commit()

    return TransactionResponse(results=results)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FinGuard Classifier Agent!"}


import json

from fastapi.responses import StreamingResponse

from classifier_agent.resources.services import get_http_client, get_llm_service


async def event_stream_generator(request: StreamRequest, db: AsyncSession, _llm, _http):
    """
    Mock generator for Task 4 to simulate the LangGraph stream.
    Yields Server-Sent Events with multi-message types (Stretch Goal 2).
    """
    # 1. Yield a status update
    yield f"data: {json.dumps({'type': 'status', 'data': 'Connecting to classifier...'})}\n\n"
    await asyncio.sleep(0.1)  # Simulate some latency

    # 2. Run the actual classification (simulating AI processing)
    category = await asyncio.to_thread(classify_transaction, request.description)

    # 3. Yield the AI message
    yield f"data: {json.dumps({'type': 'ai', 'data': {'category': category}, 'message': 'Classified'})}\n\n"

    # 4. Optional: Save to db (not strictly required for the stream test, but good practice)
    db_record = TransactionRecord(description=request.description, category=category)
    db.add(db_record)
    await db.commit()

    # 5. Yield done message
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/stream/transactions")
async def stream_transactions_endpoint(
    request: StreamRequest,
    db: AsyncSession = Depends(get_db_session_factory),
    llm=Depends(get_llm_service),
    http=Depends(get_http_client),
):
    """
    Stream Server-Sent Events (SSE) representing the progress of a transaction classification.
    """
    return StreamingResponse(event_stream_generator(request, db, llm, http), media_type="text/event-stream")
