from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
import base64
import os

from transaction_engine.classifier import get_classifier
from .models import Base, TransactionRecord


class Settings(BaseSettings):
    admin_username: str = "admin"
    admin_password: str = "fingguard123"
    database_url: str = "sqlite+aiosqlite:///./classifier.db"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

engine = create_async_engine(settings.database_url)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

app = FastAPI()


async def get_db():
    async with async_session() as session:
        yield session


async def verify_base64_auth(authorization: Optional[str] = Header(None, alias="Authorization")):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    try:
        scheme, credentials = authorization.split(" ", 1)
        if scheme.lower() != "basic":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
        decoded = base64.b64decode(credentials).decode("utf-8")
        username, password = decoded.split(":", 1)
        if username != settings.admin_username or password != settings.admin_password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except (ValueError, base64.binascii.Error):
        raise HTTPException(status_code=401, detail="Invalid authorization header")


class TransactionCreate(BaseModel):
    description: str


class TransactionUpdate(BaseModel):
    description: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    description: str
    category: str
    processed_at: datetime

    model_config = {"from_attributes": True}


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/transactions", response_model=List[TransactionResponse])
async def list_transactions(db: AsyncSession = Depends(get_db), _: None = Depends(verify_base64_auth)):
    result = await db.execute(select(TransactionRecord))
    return result.scalars().all()


@app.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(transaction_id: int, db: AsyncSession = Depends(get_db), _: None = Depends(verify_base64_auth)):
    result = await db.execute(select(TransactionRecord).where(TransactionRecord.id == transaction_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return record


@app.post("/transactions", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate, db: AsyncSession = Depends(get_db), _: None = Depends(verify_base64_auth)):
    category = get_classifier().classify_transaction(transaction.description)
    record = TransactionRecord(description=transaction.description, category=category)
    db.add(record)
    await db.commit()
    await db.refresh(record)
    return record


@app.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: int, transaction: TransactionUpdate, db: AsyncSession = Depends(get_db), _: None = Depends(verify_base64_auth)):
    result = await db.execute(select(TransactionRecord).where(TransactionRecord.id == transaction_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    if transaction.description is not None:
        record.description = transaction.description
        record.category = get_classifier().classify_transaction(transaction.description)
    
    await db.commit()
    await db.refresh(record)
    return record


@app.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: int, db: AsyncSession = Depends(get_db), _: None = Depends(verify_base64_auth)):
    result = await db.execute(select(TransactionRecord).where(TransactionRecord.id == transaction_id))
    record = result.scalar_one_or_none()
    if not record:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    await db.delete(record)
    await db.commit()
    return {"message": "Transaction deleted"}


@app.get("/")
async def read_root():
    return {"message": "Welcome to the FinGuard Classifier Agent!"}
