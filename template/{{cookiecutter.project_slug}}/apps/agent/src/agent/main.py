"""FastAPI entrypoint — mounts the AG-UI endpoint the frontend talks to."""

from __future__ import annotations

import asyncio
import sys
from contextlib import asynccontextmanager

# psycopg async (Postgres checkpointer) can't run on Windows' ProactorEventLoop.
# The policy helps any runner that honors it; for uvicorn use the loop factory
# below (`python -m agent.main`, or `uvicorn --loop agent.main:psycopg_safe_loop`)
# since uvicorn's own factory picks Proactor on win32. `myg dev` passes --reload,
# which already lands on SelectorEventLoop.
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from ag_ui_langgraph import LangGraphAgent, add_langgraph_fastapi_endpoint
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent import patterns
from agent.checkpoints import make_checkpointer
from agent.config import load_config


def psycopg_safe_loop() -> asyncio.AbstractEventLoop:
    """uvicorn custom `--loop` factory — called with zero args, must return a
    loop instance. Selector loop on Windows; uvicorn's normal choice (uvloop
    when installed) everywhere else."""
    if sys.platform == "win32":
        return asyncio.SelectorEventLoop()
    from uvicorn.loops.auto import auto_loop_factory

    return auto_loop_factory()()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Build checkpointer + graph once, then expose the AG-UI endpoint."""
    cfg = load_config()
    async with make_checkpointer(cfg) as checkpointer:
        graph = patterns.build_graph(cfg, checkpointer)
        agent = LangGraphAgent(name=cfg.app_name, graph=graph)
        add_langgraph_fastapi_endpoint(app, agent, "/agent")
        yield


app = FastAPI(title="{{ cookiecutter.project_name }} — agent", lifespan=lifespan)

# Prototype default: wide open. Restrict origins before shipping anywhere real.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health() -> dict:
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "agent.main:app",
        host="0.0.0.0",
        port=8123,
        loop="agent.main:psycopg_safe_loop",
    )
