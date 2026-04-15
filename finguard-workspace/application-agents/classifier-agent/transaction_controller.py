"""
Transaction router — POST /transactions/classify

DI chain:
    Request
      └─ get_db_session_factory()   →  Session
           └─ ClassificationService(db)
                └─ classify_many()  (transaction-engine)
                     └─ ClassifyResponse
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from classifier_agent.models import ClassifyRequest, ClassifyResponse
from classifier_agent.resources import get_db_session_factory
from classifier_agent.services import ClassificationService

router = APIRouter(prefix="/transactions", tags=["transactions"])


def _get_classification_service(
    db: Session = Depends(get_db_session_factory),
) -> ClassificationService:
    """
    Second-level dependency: builds ClassificationService with an
    already-resolved DB session. Keeps the route handler clean.
    """
    return ClassificationService(db)


@router.post(
    "/classify",
    response_model=ClassifyResponse,
    status_code=status.HTTP_200_OK,
    summary="Classify raw transactions",
    description=(
        "Accepts a list of raw transaction strings, classifies each one "
        "using the shared transaction-engine, persists the results, and "
        "returns a structured list of classified transactions."
    ),
)
def classify_transactions(
    payload: ClassifyRequest,
    service: ClassificationService = Depends(_get_classification_service),
) -> ClassifyResponse:
    return service.classify(payload.transactions)
