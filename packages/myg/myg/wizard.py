"""Interactive prompts (questionary) + LLM-assisted config for `myg init --assist`."""

from __future__ import annotations

import json

import questionary
from rich.console import Console
from rich.panel import Panel

from myg import llm
from myg.context import MODEL_SUGGESTIONS, PATTERNS, UI_STYLES, MygContext

console = Console()

_PATTERN_HELP = {
    "react": "One agent, tools, done. Fastest to grok — pick this for prototypes.",
    "plan_execute": "Planner drafts steps → executor runs them → replanner adjusts. Longer tasks.",
    "supervisor": "A boss agent delegates to subagents-as-tools. Multi-domain work.",
    "swarm": "Agents hand off to each other mid-conversation. Fluid multi-agent chat.",
    "rag": "ReAct agent + local knowledge retriever over knowledge/*.md. Doc-grounded Q&A.",
    "hitl": "ReAct agent that pauses for human approval before risky tool calls.",
    "evaluator_optimizer": "Generate → grade → revise until it passes. Quality-first answers.",
}

_ASSIST_SYSTEM = """You fill in config for 'myg', a CLI that scaffolds LangGraph agent apps.
Given the user's description, reply with ONLY a JSON object (no fences) of fields to set:
project_name (kebab-case), description, agent_pattern (react|plan_execute|supervisor|
swarm|rag|hitl|evaluator_optimizer),
system_prompt, model (provider:name, e.g. openai:gpt-4o), ui_style (default|terminal|brutalist),
primary_color, secondary_color (hex), db (neon|postgres|sqlite), gateway (off|local|konnect),
subagents (lines of 'name:prompt', only for supervisor/swarm).
Omit fields you can't infer. Sensible, stylish defaults."""


def ask(prompt: str, **kwargs) -> str:
    answer = questionary.text(prompt, **kwargs).ask()
    if answer is None:
        raise KeyboardInterrupt
    return answer.strip()


def run_wizard(ctx: MygContext) -> MygContext:
    """Classic questionary wizard — fills any fields not already set via flags."""
    console.print(Panel.fit("[bold]myg[/bold] — let's build your agent.", border_style="blue"))
    ctx.project_name = ask("Project name", default=ctx.project_name)
    ctx.description = ask("One-line description", default=ctx.description)
    ctx.agent_pattern = questionary.select(
        "Agent pattern",
        choices=[questionary.Choice(f"{p} — {_PATTERN_HELP[p]}", value=p) for p in PATTERNS],
        default=ctx.agent_pattern,
    ).ask()
    ctx.system_prompt = ask("System prompt", default=ctx.system_prompt)
    ctx.model = questionary.select(
        "Model", choices=list(MODEL_SUGGESTIONS), default=ctx.model
    ).ask()
    if ctx.agent_pattern in ("supervisor", "swarm"):
        ctx.subagents = ask(
            "Subagents (one 'name:prompt' per line)", default=ctx.subagents, multiline=True
        )
    ctx.ui_style = questionary.select(
        "UI style", choices=list(UI_STYLES), default=ctx.ui_style
    ).ask()
    ctx.primary_color = ask("Primary color (hex)", default=ctx.primary_color)
    ctx.secondary_color = ask("Secondary color (hex)", default=ctx.secondary_color)
    ctx.db = questionary.select(
        "Thread storage",
        choices=[
            questionary.Choice("neon — instant cloud Postgres, zero signup", value="neon"),
            questionary.Choice("postgres — Docker Postgres in compose", value="postgres"),
            questionary.Choice("sqlite — zero infra, file-based", value="sqlite"),
        ],
        default=ctx.db,
    ).ask()
    ctx.gateway = questionary.select(
        "AI Gateway (Kong)",
        choices=[
            questionary.Choice("off", value="off"),
            questionary.Choice("local — Kong OSS in docker-compose via decK", value="local"),
            questionary.Choice(
                "konnect — Kong Konnect cloud (needs KONNECT_TOKEN)", value="konnect"
            ),
        ],
        default=ctx.gateway,
    ).ask()
    return ctx


def run_assist(ctx: MygContext) -> MygContext:
    """LLM interview: describe the app in words → config gets filled for you."""
    if not llm.available_provider():
        console.print("[yellow]No LLM key in env — falling back to the wizard.[/yellow]")
        return run_wizard(ctx)
    brief = ask("Describe the agent app you want in a sentence or two")
    raw = llm.complete(_ASSIST_SYSTEM, brief)
    try:
        data = json.loads(raw.strip().removeprefix("```json").removesuffix("```").strip())
    except json.JSONDecodeError:
        console.print(
            "[yellow]Couldn't parse the LLM reply — starting the wizard instead.[/yellow]"
        )
        return run_wizard(ctx)
    for key, value in data.items():
        if hasattr(ctx, key) and value not in (None, ""):
            setattr(ctx, key, str(value))
    console.print("[green]Got it.[/green] Proposed config:")
    for k, v in ctx.cookiecutter_context().items():
        console.print(f"  [dim]{k}[/dim] = {v}")
    if not questionary.confirm("Looks good?", default=True).ask():
        return run_wizard(ctx)
    return ctx


def style_from_github(url: str) -> dict[str, str]:
    """Fetch a GitHub repo's CSS/tailwind config and extract theme tokens via LLM."""
    path = url.replace("https://github.com/", "").strip("/")
    candidates = [
        "src/app/globals.css",
        "app/globals.css",
        "styles/globals.css",
        "tailwind.config.ts",
        "tailwind.config.js",
        "src/index.css",
    ]
    fetched = ""
    for cand in candidates:
        raw = f"https://raw.githubusercontent.com/{path}/main/{cand}"
        try:
            resp = httpx_get(raw)
        except Exception:
            raw = f"https://raw.githubusercontent.com/{path}/master/{cand}"
            try:
                resp = httpx_get(raw)
            except Exception:
                continue
        if resp:
            fetched += f"\n--- {cand} ---\n{resp[:6000]}"
    if not fetched:
        return {}
    out = llm.complete(
        "Extract a UI theme from these stylesheets. Reply ONLY with JSON: "
        '{"ui_style": "default|terminal|brutalist", "primary_color": "#hex", '
        '"secondary_color": "#hex"}',
        fetched,
    )
    return json.loads(out.strip().removeprefix("```json").removesuffix("```").strip())


def httpx_get(url: str) -> str:
    import httpx

    resp = httpx.get(url, timeout=15, follow_redirects=True)
    return resp.text if resp.status_code == 200 else ""
