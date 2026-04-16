"""FastAPI application entry point.

All long-lived resources (DB engine, LLM service, checkpointer) are exposed
through ``Depends()`` factories in ``classifier_agent.resources``; this
module is intentionally thin so tests can override any dependency via
``app.dependency_overrides``.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from classifier_agent.controllers import agent_router, classify_router
from classifier_agent.resources.database import init_models


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    await init_models()
    yield


app = FastAPI(title="FinGuard Classifier Agent", version="0.1.0", lifespan=lifespan)
app.include_router(classify_router)
app.include_router(agent_router)


@app.get("/")
async def read_root() -> dict[str, str]:
    return {"message": "Welcome to the FinGuard Classifier Agent!"}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
