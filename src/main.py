from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.router import router as classification_router
from src.models import HealthResponse

app = FastAPI(
    title="Transaction Classification Service",
    description="Rule-based transaction classifier with SSE streaming support",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(classification_router, prefix="/api/v1", tags=["classification"])


@app.get("/health", response_model=HealthResponse)
async def health():
    return HealthResponse(status="healthy")
