import json
import os
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Protocol

from sqlalchemy import text
from sqlalchemy.engine import Engine


class Checkpointer(Protocol):
    def put(self, thread_id: str, data: dict) -> None: ...

    def get(self, thread_id: str) -> dict | None: ...


class InMemoryCheckpointer:
    def __init__(self) -> None:
        self._store: dict[str, dict] = {}

    def put(self, thread_id: str, data: dict) -> None:
        self._store[thread_id] = data

    def get(self, thread_id: str) -> dict | None:
        return self._store.get(thread_id)


@dataclass
class SqlAlchemyCheckpointer:
    engine: Engine

    def __post_init__(self) -> None:
        with self.engine.begin() as conn:
            conn.execute(
                text(
                    """
                    CREATE TABLE IF NOT EXISTS graph_checkpoints (
                        thread_id TEXT PRIMARY KEY,
                        payload TEXT NOT NULL,
                        updated_at TEXT NOT NULL
                    )
                    """
                )
            )

    def put(self, thread_id: str, data: dict) -> None:
        payload = json.dumps(data)
        now = datetime.now(UTC).isoformat()
        with self.engine.begin() as conn:
            conn.execute(text("DELETE FROM graph_checkpoints WHERE thread_id = :thread_id"), {"thread_id": thread_id})
            conn.execute(
                text(
                    """
                    INSERT INTO graph_checkpoints(thread_id, payload, updated_at)
                    VALUES (:thread_id, :payload, :updated_at)
                    """
                ),
                {"thread_id": thread_id, "payload": payload, "updated_at": now},
            )

    def get(self, thread_id: str) -> dict | None:
        with self.engine.begin() as conn:
            row = conn.execute(
                text("SELECT payload FROM graph_checkpoints WHERE thread_id = :thread_id"),
                {"thread_id": thread_id},
            ).first()

        if row is None:
            return None

        return json.loads(row[0])


def resolve_checkpointer_backend(database_url: str) -> str:
    explicit_backend = os.getenv("CHECKPOINTER_BACKEND", "auto").lower()
    if explicit_backend in {"in-memory", "memory", "sqlite", "postgres"}:
        return "in-memory" if explicit_backend in {"in-memory", "memory"} else explicit_backend

    if database_url.startswith("postgres"):
        return "postgres"
    if database_url.startswith("sqlite"):
        return "sqlite"

    return "in-memory"
