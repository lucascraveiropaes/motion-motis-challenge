from enum import Enum
from pydantic import BaseModel, Field


class Category(str, Enum):
    FOOD = "food"
    ENTERTAINMENT = "entertainment"
    OTHER = "other"


class ClassificationRequest(BaseModel):
    descriptions: list[str] = Field(..., min_length=1, max_length=1000)


class ClassificationResult(BaseModel):
    description: str
    category: Category
    confidence: float = Field(..., ge=0.0, le=1.0)


class BatchClassificationResponse(BaseModel):
    results: list[ClassificationResult]
    total: int
    processed_at: str


class StreamEvent(BaseModel):
    index: int
    description: str
    category: Category
    confidence: float
    done: bool = False


class HealthResponse(BaseModel):
    status: str
    version: str = "1.0.0"
