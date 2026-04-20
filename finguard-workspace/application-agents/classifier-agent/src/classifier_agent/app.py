from typing import List

from fastapi import Depends, FastAPI
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

# Import from the workspace package
from transaction_engine.classifier import classify_transaction

from .models import Base, TransactionRecord

# Database setup
DATABASE_URL = "sqlite:///./classifier.db"  # Using SQLite for simplicity in this example
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()


# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Pydantic models for request/response
class TransactionRequest(BaseModel):
    descriptions: List[str] = Field(..., examples=["Starbucks Coffee", "Netflix Monthly"])


class TransactionResponseItem(BaseModel):
    description: str
    category: str


class TransactionResponse(BaseModel):
    results: List[TransactionResponseItem]


@app.post("/transactions/classify", response_model=TransactionResponse)
async def classify_transactions_endpoint(request: TransactionRequest, db: Session = Depends(get_db)):
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
