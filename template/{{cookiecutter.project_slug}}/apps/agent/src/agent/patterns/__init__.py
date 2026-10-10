"""Agent pattern registry — each module exposes build_graph(cfg, checkpointer)."""

from __future__ import annotations

from typing import Callable

from langgraph.graph.state import CompiledStateGraph

from agent.config import AgentConfig
from agent.patterns import (
    evaluator_optimizer,
    hitl,
    plan_execute,
    rag,
    react,
    supervisor,
    swarm,
)

BUILDERS: dict[str, Callable[[AgentConfig, object], CompiledStateGraph]] = {
    "react": react.build_graph,
    "plan_execute": plan_execute.build_graph,
    "supervisor": supervisor.build_graph,
    "swarm": swarm.build_graph,
    "rag": rag.build_graph,
    "hitl": hitl.build_graph,
    "evaluator_optimizer": evaluator_optimizer.build_graph,
}


def build_graph(cfg: AgentConfig, checkpointer: object) -> CompiledStateGraph:
    """Dispatch to the pattern selected in myg.toml."""
    try:
        return BUILDERS[cfg.pattern](cfg, checkpointer)
    except KeyError:
        raise ValueError(f"Unknown agent pattern: {cfg.pattern!r}") from None
