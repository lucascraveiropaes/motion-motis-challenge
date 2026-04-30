from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Import from the workspace package
from transaction_engine.classifier import classify_transaction
from .models import Base, TransactionRecord
from controllers import agent_controller
from schemas.transactions import TransactionRequest, TransactionResponse, TransactionResponseItem
from resources.db_service import get_db

# Database setup
DATABASE_URL = "sqlite:///./classifier.db"  # Using SQLite for simplicity in this example
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create tables if they don't exist
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(agent_controller.router)

@app.post("/transactions/classify", response_model=TransactionResponse)
async def classify_transactions_endpoint(
    request: TransactionRequest,
    db: Session = Depends(get_db)
):
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

