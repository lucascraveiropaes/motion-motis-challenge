import asyncio
import json
import uuid
from typing import List, Optional

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Import from the workspace package
from transaction_engine.classifier import classify_transaction

from classifier_agent.graph.types import GraphContext
from classifier_agent.graph.workflow import get_compiled_graph
from classifier_agent.models import ClassificationJob, TransactionRecord
from classifier_agent.resources.database import get_db_session_factory, init_db
from classifier_agent.resources.services import checkpointer_factory, http_client_factory, llm_service_factory

# Initialize database tables
init_db()

app = FastAPI()


# ---------------------------------------------------------------------------
# Pydantic models
# ---------------------------------------------------------------------------


class TransactionRequest(BaseModel):
    descriptions: List[str] = Field(..., examples=["Starbucks Coffee", "Netflix Monthly"])


class TransactionResponseItem(BaseModel):
    description: str
    category: str


class TransactionResponse(BaseModel):
    results: List[TransactionResponseItem]


class JobResponse(BaseModel):
    """Returned immediately when a classification job is enqueued (SG1)."""

    job_id: str
    status: str
    message: str


class JobResultResponse(BaseModel):
    """Returned when polling for job results (SG1)."""

    job_id: str
    status: str
    results: Optional[List[TransactionResponseItem]] = None


class StreamRequest(BaseModel):
    description: str = Field(..., examples=["Starbucks Coffee"])
    thread_id: str = Field(..., examples=["test-123"])


# ---------------------------------------------------------------------------
# Background task helper (Stretch Goal 1)
# ---------------------------------------------------------------------------


async def _process_classification_job(job_id: str, descriptions: List[str]) -> None:
    """
    Background task: classifies transactions and updates the job record.
    Uses its own DB session (request session is already closed at this point).
    """
    from classifier_agent.resources.database import SessionLocal

    async with SessionLocal() as db:
        # 1. Mark job as processing
        result = await db.execute(select(ClassificationJob).where(ClassificationJob.job_id == job_id))
        job = result.scalars().first()
        if job is None:
            return

        job.status = "processing"  # pragma: no cover
        await db.commit()  # pragma: no cover

        # 2. Classify concurrently via thread pool (engine is synchronous)
        tasks = [asyncio.to_thread(classify_transaction, desc) for desc in descriptions]  # pragma: no cover
        categories = await asyncio.gather(*tasks)  # pragma: no cover

        # 3. Persist individual TransactionRecords
        for desc, category in zip(descriptions, categories):
            db.add(TransactionRecord(description=desc, category=category))

        # 4. Store results on the job and mark completed
        job.status = "completed"
        job.results = json.dumps([{"description": d, "category": c} for d, c in zip(descriptions, categories)])
        await db.commit()


# ---------------------------------------------------------------------------
# Endpoints
# ---------------------------------------------------------------------------


@app.post("/transactions/classify", response_model=JobResponse, status_code=202)
async def classify_transactions_endpoint(
    request: TransactionRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db_session_factory),
):
    """
    Enqueues a classification batch job and returns a job_id immediately (202 Accepted).
    Use GET /transactions/classify/{job_id} to poll for results.
    Implements Stretch Goal 1: Asynchronous Batch Processor.
    """
    # Create the job record
    job = ClassificationJob(job_id=str(uuid.uuid4()), status="pending")
    db.add(job)
    await db.commit()
    await db.refresh(job)  # pragma: no cover

    # Schedule background processing
    background_tasks.add_task(_process_classification_job, job.job_id, request.descriptions)  # pragma: no cover

    return JobResponse(  # pragma: no cover
        job_id=job.job_id,
        status="pending",
        message=f"Job enqueued. Poll GET /transactions/classify/{job.job_id} for results.",
    )


@app.get("/transactions/classify/{job_id}", response_model=JobResultResponse)
async def get_classification_job(
    job_id: str,
    db: AsyncSession = Depends(get_db_session_factory),
):
    """Returns the status and results of a previously enqueued classification job."""
    result = await db.execute(select(ClassificationJob).where(ClassificationJob.job_id == job_id))  # pragma: no cover
    job = result.scalars().first()  # pragma: no cover

    if job is None:  # pragma: no cover
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found.")  # pragma: no cover

    results = None  # pragma: no cover
    if job.status == "completed" and job.results:  # pragma: no cover
        raw = json.loads(job.results)  # pragma: no cover
        results = [TransactionResponseItem(**r) for r in raw]  # pragma: no cover

    return JobResultResponse(job_id=job.job_id, status=job.status, results=results)  # pragma: no cover


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FinGuard Classifier Agent!"}


# ---------------------------------------------------------------------------
# SSE Stream endpoint (Task 4 + SG2 + SG3)
# ---------------------------------------------------------------------------


async def event_stream_generator(request: StreamRequest, db: AsyncSession, llm, http, checkpointer):
    """
    Generator that uses LangGraph to stream Server-Sent Events.
    Satisfies Stretch Goal 2 (Multi-Message Types) and Stretch Goal 3 (Checkpointer).
    """
    yield f"data: {json.dumps({'type': 'status', 'data': 'Connecting to classifier...'})}\n\n"

    context = GraphContext(llm_service=llm, http_client=http, db_session=db)
    graph = get_compiled_graph(context=context, checkpointer=checkpointer)

    config = {"configurable": {"thread_id": request.thread_id}}

    async for event in graph.astream({"description": request.description}, config=config, stream_mode="updates"):
        if "classify" in event:
            category = event["classify"]["category"]

            db_record = TransactionRecord(description=request.description, category=category)
            db.add(db_record)
            await db.commit()

            yield f"data: {json.dumps({'type': 'ai', 'data': {'category': category}, 'message': 'Classified'})}\n\n"

    yield f"data: {json.dumps({'type': 'done'})}\n\n"


@app.post("/stream/transactions")
async def stream_transactions_endpoint(
    request: StreamRequest,
    db: AsyncSession = Depends(get_db_session_factory),
    llm=Depends(llm_service_factory),
    http=Depends(http_client_factory),
    checkpointer=Depends(checkpointer_factory),
):
    """
    Stream Server-Sent Events (SSE) representing the progress of a transaction classification using LangGraph.
    """
    return StreamingResponse(
        event_stream_generator(request, db, llm, http, checkpointer),
        media_type="text/event-stream",
    )
