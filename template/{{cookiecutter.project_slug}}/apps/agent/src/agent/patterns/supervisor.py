"""Supervisor — a lead agent delegates to subagents wrapped as tools.

This is the pattern LangChain currently recommends for multi-agent systems
(the old langgraph-supervisor package is deprecated): each specialist is a
create_agent graph invoked through a tool call by the supervisor.
"""

from __future__ import annotations

from langchain.agents import create_agent
from langchain_core.tools import StructuredTool

from agent.config import AgentConfig, SubAgent
from agent.model import build_model
from agent.tools import DEFAULT_TOOLS


def _make_worker(sa: SubAgent, cfg: AgentConfig) -> StructuredTool:
    """Compile a specialist agent and expose it to the supervisor as a tool."""
    worker = create_agent(
        model=build_model(cfg), tools=DEFAULT_TOOLS, system_prompt=sa.prompt, name=sa.name
    )

    def _call(query: str) -> str:
        out = worker.invoke({"messages": [("user", query)]})
        return out["messages"][-1].content

    return StructuredTool.from_function(
        _call,
        name=f"call_{sa.name}",
        description=f"Delegate a task to {sa.name}. Specialty: {sa.prompt}",
    )


def build_graph(cfg: AgentConfig, checkpointer):
    workers = [_make_worker(sa, cfg) for sa in cfg.subagents]
    roster = "\n".join(f"- {t.name}: {t.description}" for t in workers)
    prompt = (
        f"{cfg.system_prompt}\n\n"
        "You are the supervisor. Delegate work to specialists when it helps:\n"
        f"{roster}\n"
        "Answer directly only when no specialist is needed."
    )
    return create_agent(
        model=build_model(cfg), tools=workers, system_prompt=prompt, checkpointer=checkpointer
    )
