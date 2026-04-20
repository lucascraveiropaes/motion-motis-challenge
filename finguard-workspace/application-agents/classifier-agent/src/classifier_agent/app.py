from typing import List

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

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


@app.post("/transactions/classify", response_model=TransactionResponse)
async def classify_transactions_endpoint(request: TransactionRequest, db: Session = Depends(get_db_session_factory)):
    """
    Classifies a list of transaction descriptions and stores them in the database.
    """
    results = []
    for description in request.descriptions:
        category = classify_transaction(description)

        # Persist to database
        db_record = TransactionRecord(description=description, category=category)
        db.add(db_record)
        db.commit()
        db.refresh(db_record)

        results.append(TransactionResponseItem(description=description, category=category))

    return TransactionResponse(results=results)


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FinGuard Classifier Agent!"}
