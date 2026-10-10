"""Swarm — peer agents hand the conversation to each other via Command(goto=...)."""

from __future__ import annotations

from typing import Annotated

from langchain.agents import create_agent
from langchain_core.messages import ToolMessage
from langchain_core.tools import InjectedToolCallId, tool
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from langgraph.types import Command

from agent.config import AgentConfig
from agent.model import build_model
from agent.tools import DEFAULT_TOOLS


class SwarmState(MessagesState):
    """active_agent remembers who's talking across user turns."""

    active_agent: str


def _handoff_tool(target: str):
    """A tool the agent calls to hand the conversation to a peer agent."""

    @tool(f"transfer_to_{target}")
    def _transfer(tool_call_id: Annotated[str, InjectedToolCallId]):
        """Transfer the conversation to another agent."""
        return Command(
            goto=target,
            update={
                "active_agent": target,
                "messages": [ToolMessage(f"Transferred to {target}.", tool_call_id=tool_call_id)],
            },
            graph=Command.PARENT,
        )

    return _transfer


def build_graph(cfg: AgentConfig, checkpointer):
    names = [sa.name for sa in cfg.subagents]
    builder = StateGraph(SwarmState)
    for sa in cfg.subagents:
        handoffs = [_handoff_tool(n) for n in names if n != sa.name]
        agent = create_agent(
            model=build_model(cfg),
            tools=[*DEFAULT_TOOLS, *handoffs],
            system_prompt=(
                f"{sa.prompt}\nTransfer to a peer with transfer_to_<name> when their "
                f"specialty fits better. Peers: {', '.join(n for n in names if n != sa.name)}"
            ),
            name=sa.name,
        )
        builder.add_node(sa.name, agent)
        builder.add_edge(sa.name, END)

    def pick_entry(state: SwarmState) -> str:
        return state.get("active_agent") or names[0]

    builder.add_conditional_edges(START, pick_entry, names)
    return builder.compile(checkpointer=checkpointer)
