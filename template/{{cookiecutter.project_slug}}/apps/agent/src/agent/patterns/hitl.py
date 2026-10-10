"""Human-in-the-loop — a ReAct agent that pauses for approval on risky tools.

`HumanInTheLoopMiddleware` interrupts before the listed tools run; the pause
travels over AG-UI as an interrupt event and the run resumes with the human's
decision (approve / edit / reject) via the thread's checkpoint.

The scaffolded CopilotChat surfaces the interrupt in the stream — add a
renderAndWaitForResponse / approval component in apps/web for a polished
approve-edit-reject UI.
"""

from __future__ import annotations

from langchain.agents import create_agent
from langchain.agents.middleware import HumanInTheLoopMiddleware

from agent.config import AgentConfig
from agent.model import build_model
from agent.tools import DEFAULT_TOOLS

# Tools that must not run without a human decision. `get_current_time` stays
# auto-approved — it can't hurt anyone.
_INTERRUPT_ON = {
    "web_search": {
        "allowed_decisions": ["approve", "edit", "reject"],
        "description": "External lookup — confirm the query is appropriate.",
    },
    "get_weather": {
        "allowed_decisions": ["approve", "reject"],
        "description": "Approve before calling the weather provider.",
    },
}


def build_graph(cfg: AgentConfig, checkpointer):
    return create_agent(
        model=build_model(cfg),
        tools=DEFAULT_TOOLS,
        system_prompt=cfg.system_prompt,
        middleware=[HumanInTheLoopMiddleware(interrupt_on=_INTERRUPT_ON)],
        checkpointer=checkpointer,
    )
