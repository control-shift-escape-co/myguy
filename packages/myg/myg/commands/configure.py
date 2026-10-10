"""`myg configure` — edit myg.toml values and re-render template files in place."""

from __future__ import annotations

import subprocess
import tomllib
from pathlib import Path
from typing import Annotated

import questionary
import tomli_w
import typer
from rich.console import Console

from myg import render, wizard
from myg.context import MygContext, find_project_root

console = Console()

_FLAT_KEYS = {
    "name": "project_name",
    "pattern": "agent_pattern",
    "model": "model",
    "prompt": "system_prompt",
    "system_prompt": "system_prompt",
    "style": "ui_style",
    "db": "db",
    "gateway": "gateway",
}
_SECTION_KEYS = {
    "agent.pattern": "agent_pattern",
    "agent.model": "model",
    "agent.system_prompt": "system_prompt",
    "ui.style": "ui_style",
    "ui.primary_color": "primary_color",
    "ui.secondary_color": "secondary_color",
    "db.provider": "db",
    "gateway.mode": "gateway",
    "project.name": "project_name",
    "project.description": "description",
}


def configure(
    set_: Annotated[
        list[str] | None,
        typer.Option("--set", "-s", help="key=value, e.g. agent.pattern=supervisor"),
    ] = None,
    get: Annotated[str | None, typer.Option("--get", "-g", help="Print a config value")] = None,
    ai: Annotated[bool, typer.Option("--ai", help="Reconfigure by chatting with an LLM")] = False,
    github_style: Annotated[
        str | None, typer.Option("--github-style", help="Extract UI style from a GitHub repo")
    ] = None,
    project_dir: Annotated[Path | None, typer.Option("--dir", "-d")] = None,
    no_render: Annotated[bool, typer.Option("--no-render", help="Only update myg.toml")] = False,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip confirmation prompts")] = False,
) -> None:
    """Change config on an existing generated app."""
    root = project_dir or find_project_root()
    toml_path = root / "myg.toml"
    ctx = MygContext.from_myg_toml(toml_path)

    if get:
        key = _SECTION_KEYS.get(get, _FLAT_KEYS.get(get, get))
        console.print(getattr(ctx, key))
        raise typer.Exit()

    changed = False
    if github_style:
        with console.status(f"Extracting style from {github_style}…"):
            for key, value in wizard.style_from_github(github_style).items():
                setattr(ctx, key, value)
        changed = True
    for assignment in set_ or []:
        key, _, value = assignment.partition("=")
        attr = _SECTION_KEYS.get(key.strip(), _FLAT_KEYS.get(key.strip(), key.strip()))
        if not hasattr(ctx, attr):
            console.print(f"[red]Unknown config key: {key}[/red]")
            raise typer.Exit(2)
        setattr(ctx, attr, value.strip())
        changed = True
    if ai:
        ctx = wizard.run_assist(ctx)
        changed = True
    if not changed:
        console.print("Nothing to do — pass --set, --ai or --github-style.")
        raise typer.Exit()

    if not no_render and _git_dirty(root) and not (yes or _confirm_overwrite()):
        console.print("Aborted — nothing written.")
        raise typer.Abort()

    ctx.write_myg_toml(toml_path)
    console.print("[green]✓[/green] myg.toml updated")
    if no_render:
        return
    with console.status("Re-rendering template files…"):
        render.rerender(root, ctx.cookiecutter_context())
    console.print("[green]✓[/green] Template files re-rendered")


def _confirm_overwrite() -> bool:
    try:
        return bool(
            questionary.confirm(
                "Uncommitted changes detected — re-render may overwrite template files. Continue?",
                default=False,
            ).ask()
        )
    except Exception:
        console.print(
            "[yellow]Non-interactive shell — pass --yes to re-render over a dirty tree.[/yellow]"
        )
        return False


def _git_dirty(root: Path) -> bool:
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"], cwd=root, capture_output=True, text=True, timeout=10
        )
        return bool(out.stdout.strip())
    except Exception:
        return False


def read_db_section(root: Path) -> dict:
    data = tomllib.loads((root / "myg.toml").read_text(encoding="utf-8"))
    return data.get("db", {})


def update_db_section(root: Path, values: dict) -> None:
    path = root / "myg.toml"
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    data.setdefault("db", {}).update(values)
    path.write_text(tomli_w.dumps(data), encoding="utf-8")
