from typing import Annotated
from uuid import uuid4

from fastapi import BackgroundTasks, Depends, FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from classifier_agent.controllers.agent_controller import router as stream_router
from classifier_agent.models import TransactionRecord
from classifier_agent.resources import checkpointer_factory, get_db_session_factory, get_session_maker
from classifier_agent.services import ClassificationService

app = FastAPI()
app.include_router(stream_router)


class TransactionRequest(BaseModel):
    descriptions: list[str] = Field(
        ...,
        json_schema_extra={"example": ["Starbucks Coffee", "Netflix Monthly"]},
    )


class TransactionResponseItem(BaseModel):
    description: str
    category: str


class TransactionResponse(BaseModel):
    results: list[TransactionResponseItem]


class AsyncClassificationResponse(BaseModel):
    job_id: str
    status: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    results: list[TransactionResponseItem] | None = None
    error: str | None = None


def _job_key(job_id: str) -> str:
    return f"job:{job_id}"


def _run_batch_job(job_id: str, descriptions: list[str]) -> None:
    checkpointer = checkpointer_factory()
    session = get_session_maker()()
    service = ClassificationService()

    try:
        results: list[dict[str, str]] = []
        for description in descriptions:
            category = service.classify(description)
            session.add(TransactionRecord(description=description, category=category))
            session.commit()
            results.append({"description": description, "category": category})

        checkpointer.put(_job_key(job_id), {"status": "completed", "results": results})
    except Exception as exc:  # pragma: no cover
        checkpointer.put(_job_key(job_id), {"status": "failed", "error": str(exc)})
    finally:
        session.close()


@app.post("/transactions/classify", response_model=TransactionResponse)
async def classify_transactions_endpoint(
    request: TransactionRequest,
    db: Annotated[Session, Depends(get_db_session_factory)],
):
    service = ClassificationService()
    results: list[TransactionResponseItem] = []

    for description in request.descriptions:
        category = service.classify(description)

        db_record = TransactionRecord(description=description, category=category)
        db.add(db_record)
        db.commit()

        results.append(TransactionResponseItem(description=description, category=category))

    return TransactionResponse(results=results)


@app.post("/transactions/classify/async", response_model=AsyncClassificationResponse)
async def classify_transactions_async_endpoint(
    request: TransactionRequest,
    background_tasks: BackgroundTasks,
) -> AsyncClassificationResponse:
    job_id = uuid4().hex
    checkpointer_factory().put(_job_key(job_id), {"status": "queued", "results": []})
    background_tasks.add_task(_run_batch_job, job_id, request.descriptions)
    return AsyncClassificationResponse(job_id=job_id, status="queued")


@app.get("/transactions/classify/jobs/{job_id}", response_model=JobStatusResponse)
async def get_batch_job_status(job_id: str) -> JobStatusResponse:
    payload = checkpointer_factory().get(_job_key(job_id))
    if payload is None:
        raise HTTPException(status_code=404, detail="Job not found")

    results_payload = payload.get("results")
    results = None
    if isinstance(results_payload, list):
        results = [TransactionResponseItem(**item) for item in results_payload]

    return JobStatusResponse(
        job_id=job_id,
        status=payload.get("status", "unknown"),
        results=results,
        error=payload.get("error"),
    )


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to the FinGuard Classifier Agent!"}
