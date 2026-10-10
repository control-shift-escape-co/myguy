"""`myg db` — instant Neon Postgres for a generated project."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.panel import Panel

from myg import neon
from myg.commands.configure import read_db_section, update_db_section
from myg.context import find_project_root

console = Console()


def db(
    db_id: Annotated[
        str | None, typer.Option("--status", help="Check status of a provisioned DB id")
    ] = None,
    project_dir: Annotated[Path | None, typer.Option("--dir", "-d")] = None,
) -> None:
    """Provision an instant Neon Postgres (no account needed) and wire it into .env."""
    if db_id:
        console.print_json(data=neon.status(db_id))
        raise typer.Exit()

    root = project_dir or find_project_root()
    with console.status("Provisioning instant Neon Postgres…"):
        ndb = neon.provision(ref=root.name)
    env_file = neon.write_database_url(root, ndb.connection_string)
    update_db_section(
        root,
        {
            "provider": "neon",
            "project_id": ndb.id,
            "claim_url": ndb.claim_url,
            "expires_at": ndb.expires_at,
        },
    )
    console.print(f"[green]✓[/green] DATABASE_URL written to {env_file}")
    console.print(
        Panel(
            f"[bold]This DB expires in 72h unless claimed.[/bold]\n\n"
            "Claim it (free Neon account, no card):\n"
            f"[link={ndb.claim_url}]{ndb.claim_url}[/link]\n\n"
            f"DB id: {ndb.id}  (check later: myg db --status {ndb.id})",
            title="⚡ instant postgres",
            border_style="yellow",
        )
    )


def claim_url(project_dir: Annotated[Path | None, typer.Option("--dir", "-d")] = None) -> None:
    """Reprint the claim URL stored in myg.toml."""
    root = project_dir or find_project_root()
    info = read_db_section(root)
    url = info.get("claim_url")
    if not url:
        console.print("[yellow]No claim URL recorded — run `myg db` first.[/yellow]")
        raise typer.Exit(1)
    console.print(url)
