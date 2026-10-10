"""`myg doctor` — environment sanity check before/after `myg init`."""

from __future__ import annotations

import os
import shutil
import socket
from pathlib import Path
from typing import Annotated

import httpx
import typer
from rich.console import Console
from rich.table import Table

from myg.context import find_project_root

console = Console()


def doctor(project_dir: Annotated[Path | None, typer.Option("--dir", "-d")] = None) -> None:
    """Check tools, keys and ports."""
    checks = [
        ("docker", "Docker (compose path)", shutil.which("docker") is not None, False),
        ("uv", "uv (native dev + uvx installs)", shutil.which("uv") is not None, False),
        ("node", "Node.js (native dev)", shutil.which("node") is not None, False),
        (
            "pnpm|npm",
            "JS package manager",
            bool(shutil.which("pnpm") or shutil.which("npm")),
            False,
        ),
        ("git", "git", shutil.which("git") is not None, True),
        (
            "LLM key",
            "ANTHROPIC/OPENAI/GEMINI in env",
            any(os.getenv(k) for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY")),
            True,
        ),
        ("port 3000", "web", _port_free(3000), True),
        ("port 8123", "agent", _port_free(8123), True),
    ]
    try:
        httpx.head("https://pypi.org", timeout=5)
        net = True
    except Exception:
        net = False
    checks.append(("network", "registry reachability", net, True))

    table = Table(title="myg doctor")
    table.add_column("check")
    table.add_column("detail")
    table.add_column("status")
    failed = 0
    for name, detail, ok, required in checks:
        table.add_row(
            name,
            detail,
            (
                "[green]ok[/green]"
                if ok
                else ("[red]missing[/red]" if required else "[yellow]optional[/yellow]")
            ),
        )
        failed += required and not ok
    console.print(table)
    if failed:
        raise typer.Exit(1)

    try:
        root = find_project_root(project_dir)
        console.print(f"[dim]project detected: {root}[/dim]")
    except FileNotFoundError:
        console.print("[dim]no generated project in this directory tree[/dim]")


def _port_free(port: int) -> bool:
    with socket.socket() as s:
        return s.connect_ex(("127.0.0.1", port)) != 0
