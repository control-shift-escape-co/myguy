"""ReAct pattern — a single tool-calling agent. Best default for prototypes."""

from __future__ import annotations

from langchain.agents import create_agent

from agent.config import AgentConfig
from agent.model import build_model
from agent.tools import DEFAULT_TOOLS


def build_graph(cfg: AgentConfig, checkpointer):
    return create_agent(
        model=build_model(cfg),
        tools=DEFAULT_TOOLS,
        system_prompt=cfg.system_prompt,
        checkpointer=checkpointer,
    )
