"""REST controller for the synchronous classify endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from classifier_agent.models import TransactionRequest, TransactionResponse
from classifier_agent.resources import get_db_session_factory, llm_service_factory
from classifier_agent.services import ClassificationService
from classifier_agent.services.llm_service import LLMService

router = APIRouter(tags=["classify"])


@router.post("/transactions/classify", response_model=TransactionResponse)
async def classify_transactions(
    request: TransactionRequest,
    db_session: AsyncSession = Depends(get_db_session_factory),
    llm_service: LLMService = Depends(llm_service_factory),
) -> TransactionResponse:
    """Classify descriptions and persist each result for auditing."""
    service = ClassificationService(llm_service=llm_service, db_session=db_session)
    results = await service.classify_and_store(request.descriptions)
    return TransactionResponse(results=results)
