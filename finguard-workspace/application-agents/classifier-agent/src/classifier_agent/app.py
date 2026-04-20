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


import asyncio
from sqlalchemy.ext.asyncio import AsyncSession

@app.post("/transactions/classify", response_model=TransactionResponse)
async def classify_transactions_endpoint(request: TransactionRequest, db: AsyncSession = Depends(get_db_session_factory)):
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
