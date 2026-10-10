"""`myg deploy` — ship the generated app to Railway."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from myg.context import find_project_root

console = Console()


def deploy(project_dir: Annotated[Path | None, typer.Option("--dir", "-d")] = None) -> None:
    """Deploy to Railway — uses the railway CLI if installed, else prints the guide."""
    root = (project_dir or find_project_root()).resolve()
    if shutil.which("railway"):
        console.print("Handing off to [bold]railway up[/bold] — follow its prompts.")
        raise typer.Exit(subprocess.run(["railway", "up"], cwd=root).returncode)
    console.print(
        Panel(
            "Railway CLI not found — no problem, the dashboard flow is 2 minutes:\n\n"
            "1. Push this project to GitHub\n"
            "2. railway.app → New Project → Deploy from GitHub repo\n"
            "3. Add TWO services with root dirs: "
            "[bold]apps/web[/bold] and [bold]apps/agent[/bold]\n"
            "4. Add a Postgres plugin (or reuse Neon) → set DATABASE_URL on agent\n"
            "5. Set env vars on each service (see .env.example + RAILWAY.md)\n\n"
            "Or: npm i -g @railway/cli && railway login && myg deploy",
            title="deploy to railway",
            border_style="blue",
        )
    )
