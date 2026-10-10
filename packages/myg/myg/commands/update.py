"""`myg update` — pull template upgrades into an existing project (cruft)."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from cruft import update as cruft_update
from rich.console import Console

from myg.context import find_project_root

console = Console()


def update(
    project_dir: Annotated[Path | None, typer.Option("--dir", "-d")] = None,
    check_only: Annotated[
        bool, typer.Option("--check", help="Only report whether an update exists")
    ] = False,
) -> None:
    """Apply template updates released since the project was generated."""
    root = (project_dir or find_project_root()).resolve()
    if check_only:
        from cruft import check

        raise typer.Exit(0 if check(project_dir=root) else 1)
    updated = cruft_update(project_dir=root)
    console.print("[green]✓[/green] Updated" if updated else "Already up to date.")
