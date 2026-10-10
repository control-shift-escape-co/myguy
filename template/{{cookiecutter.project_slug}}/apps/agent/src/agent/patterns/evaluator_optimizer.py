"""Evaluator-optimizer — generate → grade → revise loop.

The generator drafts a reply; the evaluator grades it with structured output
and returns actionable feedback; the loop repeats until the draft passes or
`MAX_LOOPS` is hit, after which the last draft ships anyway.

Use for tasks where quality is gradable: copy, summaries, code explanations.
Not for open-ended chat — the extra model call per turn costs latency.
"""

from __future__ import annotations

from typing import Literal

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from pydantic import BaseModel, Field

from agent.config import AgentConfig
from agent.model import build_model

MAX_LOOPS = 3


class EvalState(MessagesState):
    """draft = latest attempt; feedback drives the next revision; loops bounds retries."""

    draft: str
    feedback: str
    loops: int
    done: bool


class Grade(BaseModel):
    """The evaluator's verdict on the current draft."""

    passed: bool = Field(description="True if the draft fully satisfies the request")
    feedback: str = Field(
        description="Specific, actionable criticism to improve the draft (empty if passed)"
    )


_EVALUATE_PROMPT = """You are a strict evaluator. Grade the draft against the user's request.
Pass only if it is accurate, complete, and well-structured. Otherwise return
concrete feedback the writer can act on in one revision."""


def build_graph(cfg: AgentConfig, checkpointer):
    writer = build_model(cfg)
    evaluator = build_model(cfg).with_structured_output(Grade)

    async def generate(state: EvalState) -> dict:
        request = state["messages"][-1].content
        msgs: list = [SystemMessage(content=cfg.system_prompt)]
        if state.get("feedback"):
            msgs.append(
                HumanMessage(
                    content=f"Request: {request}\n\nPrevious draft:\n{state['draft']}\n\n"
                    f"Evaluator feedback — fix all of it:\n{state['feedback']}"
                )
            )
        else:
            msgs.append(HumanMessage(content=request))
        resp = await writer.ainvoke(msgs)
        return {"draft": resp.content, "loops": state.get("loops", 0) + 1, "done": False}

    async def evaluate(state: EvalState) -> dict:
        grade = await evaluator.ainvoke(
            [
                SystemMessage(content=_EVALUATE_PROMPT),
                HumanMessage(
                    content=f"Request: {state['messages'][-1].content}\n\nDraft:\n{state['draft']}"
                ),
            ]
        )
        if grade.passed or state["loops"] >= MAX_LOOPS:
            return {"done": True, "messages": [AIMessage(content=state["draft"])]}
        return {"feedback": grade.feedback}

    def route(state: EvalState) -> Literal["generate", "__end__"]:
        return END if state.get("done") else "generate"

    builder = StateGraph(EvalState)
    builder.add_node("generate", generate)
    builder.add_node("evaluate", evaluate)
    builder.add_edge(START, "generate")
    builder.add_edge("generate", "evaluate")
    builder.add_conditional_edges("evaluate", route, ["generate", END])
    return builder.compile(checkpointer=checkpointer)
