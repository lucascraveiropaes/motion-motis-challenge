"""Alembic env wired to the classifier-agent's sync DB URL.

Alembic runs migrations synchronously; we reuse the sync URL from
``AppSettings.sync_database_url`` so local SQLite dev and Postgres prod are
both covered without maintaining a second connection string.
"""

from __future__ import annotations

import os
import sys
from logging.config import fileConfig
from pathlib import Path

from alembic import context
from sqlalchemy import engine_from_config, pool

# Make the classifier_agent package importable regardless of where alembic
# is invoked from (project root, agent dir, or monorepo root).
_SRC = Path(__file__).resolve().parents[2]
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))

from classifier_agent.models import Base  # noqa: E402
from classifier_agent.settings import get_settings  # noqa: E402

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Allow overriding via env var for CI without editing the ini file.
config.set_main_option("sqlalchemy.url", os.environ.get("FINGUARD_SYNC_DATABASE_URL", get_settings().sync_database_url))

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=config.get_main_option("sqlalchemy.url"),
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
