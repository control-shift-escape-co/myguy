"""Thread persistence: Postgres (neon/docker) or SQLite — chosen by myg.toml."""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path
from typing import AsyncIterator

from langgraph.checkpoint.base import BaseCheckpointSaver

from agent.config import AgentConfig


@asynccontextmanager
async def make_checkpointer(cfg: AgentConfig) -> AsyncIterator[BaseCheckpointSaver]:
    """Yield a ready checkpointer. Postgres savers need .setup() once for tables."""
    if cfg.db_provider == "sqlite":
        from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

        path = Path("data/checkpoints.db")
        path.parent.mkdir(parents=True, exist_ok=True)
        async with AsyncSqliteSaver.from_conn_string(str(path)) as saver:
            yield saver
    else:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        if not cfg.database_url:
            raise RuntimeError(
                "DATABASE_URL is required for db=postgres/neon — set it in .env "
                "(run `myg db` to provision one instantly)."
            )
        async with AsyncPostgresSaver.from_conn_string(cfg.database_url) as saver:
            await saver.setup()
            yield saver
