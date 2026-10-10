"""`myg eject` — sever the link to the myg template.

After eject the project is plain code: `myg update` can no longer apply
template upgrades and `myg configure` can't re-render over your files.
myg.toml stays — the agent reads it at runtime — but it's just config now.
"""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import questionary
import typer
from rich.console import Console

from myg.context import find_project_root

console = Console()


def eject(
    project_dir: Annotated[Path | None, typer.Option("--dir", "-d")] = None,
    yes: Annotated[bool, typer.Option("--yes", "-y", help="Skip the confirmation")] = False,
) -> None:
    """Cut the project loose from the template — no more `myg update`."""
    root = (project_dir or find_project_root()).resolve()
    cruft = root / ".cruft.json"
    if not cruft.exists():
        console.print("[dim]Already ejected — no .cruft.json link found.[/dim]")
        raise typer.Exit()

    if (
        not yes
        and not questionary.confirm(
            "Eject removes the template link (.cruft.json). `myg update` and "
            "`myg configure` re-renders will stop working. Continue?",
            default=False,
        ).ask()
    ):
        raise typer.Abort()

    cruft.unlink()
    console.print(
        "[green]✓[/green] Ejected — this project is now yours alone.\n"
        "[dim]myg.toml stays: the agent loads it at runtime (config.py). "
        "Commands that don't touch the template — db, dev, deploy, prompt — "
        "keep working.[/dim]"
    )
