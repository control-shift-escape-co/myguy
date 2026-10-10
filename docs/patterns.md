# Agent patterns

Every pattern lives in `apps/agent/src/agent/patterns/` and exposes
`build_graph(cfg, checkpointer) -> CompiledStateGraph`. Swap anytime:
`myg configure --set agent.pattern=<name>`.

## react

`create_agent` tool loop — model ↔ tools until a final answer. Use for:
prototypes, single-domain tasks, when you want the fewest moving parts.

## plan_execute

planner → executor → replanner.

1. **planner** (structured output) decomposes the request into steps
2. **execute** runs `plan[0]` through a ReAct sub-agent with tools
3. **replan** returns the final `Response` or a revised `Plan`

Use for: long-horizon tasks where a single agent loses the plot.

## supervisor

The current LangChain-recommended multi-agent shape: each subagent is a
compiled `create_agent` wrapped in a `StructuredTool`; the supervisor agent
delegates via tool calls. (The `langgraph-supervisor` package is deprecated —
this is its successor pattern.) Configure specialists in `myg.toml`:

```toml
[agent]
subagents = """
researcher:Research the topic thoroughly.
writer:Turn research into polished prose.
"""
```

## swarm

Peer agents hand off mid-conversation via `transfer_to_<name>` tools returning
`Command(goto=...)`. `active_agent` persists in state so follow-ups resume with
the last speaker. Use for: fluid multi-persona assistants, e.g. sales → support
→ billing handoffs.

## rag

A ReAct agent with a `search_knowledge_base` tool over `knowledge/*.md|txt` in
your project root. The retriever is dependency-free keyword scoring (BM25-lite)
so it works with zero extra infra — swap `_retrieve` for a real vector store
(pgvector is a natural fit; you already have Postgres) when the corpus grows.
Use for: doc-grounded Q&A, support bots, internal knowledge assistants.

## hitl

Human-in-the-loop: a ReAct agent wrapped in `HumanInTheLoopMiddleware` that
interrupts before risky tools (`web_search`, `get_weather`) and waits for an
approve / edit / reject decision. The pause travels over AG-UI as an interrupt
and resumes from the thread checkpoint. Use for: agents with side-effecting
tools — anything that sends, buys, deletes, or deploys.

!!! note
    The scaffolded `CopilotChat` shows the interrupt in the stream; add a
    `renderAndWaitForResponse` component in `apps/web` for a proper
    approve-edit-reject UI.

## evaluator_optimizer

generate → grade → revise loop: the writer drafts, an evaluator grades with
structured output and returns feedback, and the graph loops until the draft
passes or `MAX_LOOPS` (3) is hit. Use for: gradable tasks — copy, summaries,
reports — where the extra model call is worth the quality jump. Not for
open-ended chat.
