from pydantic import BaseModel, Field
from typing import List



# Pydantic models for request/response
class TransactionRequest(BaseModel):
    descriptions: List[str] = Field(..., example=["Starbucks Coffee", "Netflix Monthly"])

class TransactionResponseItem(BaseModel):
    description: str
    category: str

class TransactionResponse(BaseModel):
    results: List[TransactionResponseItem]