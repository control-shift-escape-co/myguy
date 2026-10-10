"""`myg templates` — list built-in and community templates."""

from __future__ import annotations

from typing import Annotated

import httpx
import typer
from rich.console import Console
from rich.table import Table

from myg.context import PATTERNS

console = Console()

REGISTRY_URL = "https://raw.githubusercontent.com/control-shift-escape-co/myguy/main/template/templates-registry.json"

BUILTIN = [
    (
        "default",
        "github.com/control-shift-escape-co/myguy",
        "The full myg template — web + agent + infra",
    ),
]


def templates(community: Annotated[bool, typer.Option("--community", "-c")] = False) -> None:
    """Show available templates. Use any with `myg init --template <url>`."""
    table = Table(title="templates")
    table.add_column("name")
    table.add_column("source")
    table.add_column("notes")
    for name, source, notes in BUILTIN:
        table.add_row(name, source, notes)
    for p in PATTERNS:
        table.add_row(f"pattern:{p}", "built-in", f"default template with --pattern {p}")
    if community:
        try:
            for entry in httpx.get(REGISTRY_URL, timeout=10).json():
                table.add_row(entry["name"], entry["source"], entry.get("notes", ""))
        except Exception:
            console.print("[dim]community registry unreachable[/dim]")
    console.print(table)
