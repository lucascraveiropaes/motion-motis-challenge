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

    response_data = TransactionResponse(results=results)  # pragma: no cover
    return response_data  # pragma: no cover


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FinGuard Classifier Agent!"}


import json

from fastapi.responses import StreamingResponse

from classifier_agent.graph.types import GraphContext
from classifier_agent.graph.workflow import get_compiled_graph
from classifier_agent.resources.services import checkpointer_factory, http_client_factory, llm_service_factory


async def event_stream_generator(request: StreamRequest, db: AsyncSession, llm, http, checkpointer):
    """
    Generator that uses LangGraph to stream Server-Sent Events.
    Satisfies Stretch Goal 2 (Multi-Message Types) and Stretch Goal 3 (Checkpointer).
    """
    # 1. Yield initial status
    yield f"data: {json.dumps({'type': 'status', 'data': 'Connecting to classifier...'})}\n\n"
    
    # 2. Setup the Context and compile the Graph
    context = GraphContext(llm_service=llm, http_client=http, db_session=db)
    graph = get_compiled_graph(context=context, checkpointer=checkpointer)
    
    # 3. Stream from the graph
    # Checkpointer requires a thread_id in config
    config = {"configurable": {"thread_id": request.thread_id}}
    
    async for event in graph.astream({"description": request.description}, config=config, stream_mode="updates"):
        # The node returns {"category": <category>} in the state update.
        if "classify" in event:
            category = event["classify"]["category"]
            
            # Save to db dynamically
            db_record = TransactionRecord(description=request.description, category=category)
            db.add(db_record)
            await db.commit()
            
            # Yield the AI message
            yield f"data: {json.dumps({'type': 'ai', 'data': {'category': category}, 'message': 'Classified'})}\n\n"
            
    # 4. Yield done message
    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/stream/transactions")
async def stream_transactions_endpoint(
    request: StreamRequest,
    db: AsyncSession = Depends(get_db_session_factory),
    llm=Depends(llm_service_factory),
    http=Depends(http_client_factory),
    checkpointer=Depends(checkpointer_factory)
):
    """
    Stream Server-Sent Events (SSE) representing the progress of a transaction classification using LangGraph.
    """
    return StreamingResponse(
        event_stream_generator(request, db, llm, http, checkpointer),
        media_type="text/event-stream"
    )
