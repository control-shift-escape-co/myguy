"""`myg init` — wizard → render → optional instant Neon DB → next steps."""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Annotated

import tomli_w
import typer
from rich.console import Console
from rich.panel import Panel

from myg import neon, render, wizard
from myg.context import MygContext

console = Console()


def init(
    project_name: Annotated[str | None, typer.Argument(help="Directory + project name")] = None,
    output_dir: Annotated[Path, typer.Option("--output-dir", "-o", help="Parent directory")] = Path(
        "."
    ),
    yes: Annotated[
        bool, typer.Option("--yes", "-y", help="Skip the wizard, use flags/defaults")
    ] = False,
    defaults: Annotated[bool, typer.Option("--defaults", help="Alias for --yes")] = False,
    assist: Annotated[
        bool, typer.Option("--assist", help="Describe the app; an LLM fills the config")
    ] = False,
    pattern: Annotated[
        str | None,
        typer.Option(
            "--pattern",
            help="react|plan_execute|supervisor|swarm|rag|hitl|evaluator_optimizer",
        ),
    ] = None,
    model: Annotated[
        str | None, typer.Option("--model", help="provider:model, e.g. openai:gpt-4o")
    ] = None,
    system_prompt: Annotated[str | None, typer.Option("--system-prompt")] = None,
    subagents: Annotated[
        str | None, typer.Option("--subagents", help="One 'name:prompt' per line")
    ] = None,
    db: Annotated[str | None, typer.Option("--db", help="neon|postgres|sqlite")] = None,
    gateway: Annotated[str | None, typer.Option("--gateway", help="off|local|konnect")] = None,
    ui_style: Annotated[
        str | None, typer.Option("--ui-style", help="default|terminal|brutalist")
    ] = None,
    primary_color: Annotated[str | None, typer.Option("--primary-color")] = None,
    secondary_color: Annotated[str | None, typer.Option("--secondary-color")] = None,
    github_style: Annotated[
        str | None,
        typer.Option("--github-style", help="GitHub repo URL to crib the visual style from"),
    ] = None,
    description: Annotated[str | None, typer.Option("--description")] = None,
    template: Annotated[
        str | None, typer.Option("--template", help="Template repo URL/path (community templates)")
    ] = None,
    no_provision: Annotated[
        bool, typer.Option("--no-provision", help="Skip Neon DB provisioning")
    ] = False,
    dry_run: Annotated[
        bool, typer.Option("--dry-run", help="Show resolved config, render nothing")
    ] = False,
) -> None:
    """Scaffold a new agent app."""
    ctx = MygContext()
    for key, value in {
        "agent_pattern": pattern,
        "model": model,
        "system_prompt": system_prompt,
        "subagents": subagents,
        "db": db,
        "gateway": gateway,
        "ui_style": ui_style,
        "primary_color": primary_color,
        "secondary_color": secondary_color,
        "description": description,
        "project_name": project_name,
    }.items():
        if value is not None:
            setattr(ctx, key, value)

    try:
        if github_style:
            with console.status(f"Extracting style from {github_style}…"):
                for key, value in wizard.style_from_github(github_style).items():
                    setattr(ctx, key, value)
            console.print(
                "[green]Style extracted:[/green]",
                ctx.primary_color,
                ctx.secondary_color,
                ctx.ui_style,
            )
        if assist:
            ctx = wizard.run_assist(ctx)
        elif not (yes or defaults):
            ctx = wizard.run_wizard(ctx)
    except KeyboardInterrupt:
        raise typer.Abort() from None

    if dry_run:
        console.print(
            Panel.fit(
                "\n".join(f"{k} = {v}" for k, v in ctx.cookiecutter_context().items()),
                title="dry run",
            )
        )
        raise typer.Exit()

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    with console.status("Rendering template…"):
        dest = render.create_project(ctx.cookiecutter_context(), output_dir, template)
    ctx.write_myg_toml(dest / "myg.toml")
    console.print(f"[green]✓[/green] Generated [bold]{dest}[/bold]")

    if ctx.db == "neon" and not no_provision:
        try:
            with console.status("Provisioning instant Neon Postgres…"):
                ndb = neon.provision(ref=ctx.project_slug)
            neon.write_database_url(dest, ndb.connection_string)
            _record_db(dest / "myg.toml", ndb)
            console.print(
                Panel(
                    "DATABASE_URL written to .env\n\n"
                    "[bold yellow]Claim this DB (keeps it past 72h):[/bold yellow]\n"
                    f"{ndb.claim_url}",
                    title="neon postgres",
                    border_style="yellow",
                )
            )
        except Exception as exc:
            console.print(f"[yellow]Neon provision failed ({exc}). Run `myg db` later.[/yellow]")

    steps = [
        f"cd {dest.name}",
        "fill in .env (LLM key at minimum)",
        "docker compose up  # or: myg dev",
    ]
    if ctx.gateway == "konnect":
        steps.append("bash infra/konnect/setup-konnect.sh")
    steps += ["open http://localhost:3000"]
    console.print(
        Panel(
            "\n".join(f"{i}. {s}" for i, s in enumerate(steps, 1)),
            title="next steps",
            border_style="blue",
        )
    )


def _record_db(myg_toml: Path, ndb: neon.NeonDatabase) -> None:
    data = tomllib.loads(myg_toml.read_text(encoding="utf-8")) if myg_toml.exists() else {}
    data.setdefault("db", {}).update(
        {
            "provider": "neon",
            "project_id": ndb.id,
            "claim_url": ndb.claim_url,
            "expires_at": ndb.expires_at,
        }
    )
    myg_toml.write_text(tomli_w.dumps(data), encoding="utf-8")
