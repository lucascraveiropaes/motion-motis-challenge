from datetime import datetime, timezone

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from src.models import ClassificationRequest, BatchClassificationResponse, StreamEvent
from src.service import classifier, CLASSIFICATION_RULES

router = APIRouter()


@router.post("/classify/stream", response_class=StreamingResponse)
async def classify_stream(request: ClassificationRequest):
    async def event_generator():
        descriptions = request.descriptions
        async for idx, result in enumerate(classifier.classify_stream(descriptions)):
            is_last = idx == len(descriptions) - 1
            event = StreamEvent(
                index=idx,
                description=result.description,
                category=result.category,
                confidence=result.confidence,
                done=is_last,
            )
            yield {
                "event": "classification",
                "data": event.model_dump_json(),
            }

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/classify", response_model=BatchClassificationResponse)
async def classify_batch(request: ClassificationRequest):
    results = classifier.classify_batch(request.descriptions)
    return BatchClassificationResponse(
        results=results,
        total=len(results),
        processed_at=datetime.now(timezone.utc).isoformat(),
    )


@router.get("/rules")
async def get_rules():
    return {
        category.value: [pattern for pattern, _ in patterns]
        for category, patterns in CLASSIFICATION_RULES.items()
    }
