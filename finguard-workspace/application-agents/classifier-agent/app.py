"""
classifier-agent FastAPI application entry point.
"""
import uvicorn
from fastapi import FastAPI

from classifier_agent.controllers.agent_controller import router as agent_router
from classifier_agent.controllers.transaction_controller import router as transaction_router

app = FastAPI(
    title="Classifier Agent",
    version="0.1.0",
    description="AI-powered transaction classification service.",
)

# ---------------------------------------------------------------------------
# Routers
# ---------------------------------------------------------------------------

app.include_router(agent_router)
app.include_router(transaction_router)


# ---------------------------------------------------------------------------
# Dev entrypoint  (uv run serve)
# ---------------------------------------------------------------------------

def start() -> None:
    uvicorn.run("classifier_agent.app:app", host="0.0.0.0", port=8000, reload=True)
