"""Plan-and-execute — planner → executor → replanner loop for multi-step tasks."""

from __future__ import annotations

import operator
from typing import Annotated, Literal, TypedDict, Union

from langchain.agents import create_agent
from langchain_core.messages import AIMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import MessagesState
from pydantic import BaseModel, Field

from agent.config import AgentConfig
from agent.model import build_model
from agent.tools import DEFAULT_TOOLS


class PlanExecuteState(MessagesState):
    """messages carry the chat; plan/past_steps drive the loop; response is final."""

    plan: list[str]
    past_steps: Annotated[list[tuple[str, str]], operator.add]
    response: str


class Plan(BaseModel):
    """Steps the executor should work through, in order."""

    steps: list[str]


class Act(BaseModel):
    """The replanner either returns the final answer or a revised plan."""

    action: Union["Response", "Plan"] = Field(
        description="Response to finish, or Plan with the remaining steps."
    )


class Response(BaseModel):
    response: str


def build_graph(cfg: AgentConfig, checkpointer):
    model = build_model(cfg)
    executor_agent = create_agent(model=model, tools=DEFAULT_TOOLS, system_prompt=cfg.system_prompt)
    planner = model.with_structured_output(Plan)
    replanner = model.with_structured_output(Act)

    async def plan_step(state: PlanExecuteState):
        goal = state["messages"][-1].content
        plan = await planner.ainvoke(
            [
                (
                    "system",
                    "Break the user's request into the smallest number of concrete steps "
                    "needed to answer it fully. Reply with the ordered steps only.",
                ),
                ("user", goal),
            ]
        )
        return {"plan": plan.steps}

    async def execute_step(state: PlanExecuteState):
        step = state["plan"][0]
        done = "\n".join(f"- {s}: {r}" for s, r in state.get("past_steps", []))
        task = f"Current step: {step}\nCompleted so far:\n{done or 'nothing yet'}"
        result = await executor_agent.ainvoke({"messages": [("user", task)]})
        return {"past_steps": [(step, result["messages"][-1].content)]}

    async def replan_step(state: PlanExecuteState):
        done = "\n".join(f"- {s}: {r}" for s, r in state.get("past_steps", []))
        remaining = state["plan"][1:]
        act = await replanner.ainvoke(
            [
                (
                    "system",
                    "You are a replanner. Given the original objective, completed steps and "
                    "remaining plan: return a Response with the final answer if the objective "
                    "is met, otherwise return a Plan with any remaining/adjusted steps.",
                ),
                (
                    "user",
                    f"Objective: {state['messages'][-1].content}\n"
                    f"Remaining plan: {remaining}\nCompleted:\n{done}",
                ),
            ]
        )
        if isinstance(act.action, Response):
            answer = act.action.response
            return {"response": answer, "messages": [AIMessage(content=answer)]}
        return {"plan": act.action.steps}

    def should_end(state: PlanExecuteState) -> Literal["execute", "__end__"]:
        return END if state.get("response") else "execute"

    builder = StateGraph(PlanExecuteState)
    builder.add_node("planner", plan_step)
    builder.add_node("execute", execute_step)
    builder.add_node("replan", replan_step)
    builder.add_edge(START, "planner")
    builder.add_edge("planner", "execute")
    builder.add_edge("execute", "replan")
    builder.add_conditional_edges("replan", should_end, ["execute", END])
    return builder.compile(checkpointer=checkpointer)
