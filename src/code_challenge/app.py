"""Composition root da aplicacao FastAPI."""

from __future__ import annotations

from fastapi import FastAPI

from .api import router


def create_app() -> FastAPI:
    """Cria app e registra as rotas da API."""
    app = FastAPI(title="Code Challenge API", version="0.1.0")
    app.include_router(router)
    return app


app = create_app()
