"""`myg dev` — run the generated app: docker compose when available, else natively."""

from __future__ import annotations

import shutil
import signal
import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from myg.context import find_project_root

console = Console()


def dev(
    detach: Annotated[bool, typer.Option("-d", "--detach", help="Compose in background")] = False,
    project_dir: Annotated[Path | None, typer.Option("--dir", "-d")] = None,
) -> None:
    """Start the generated app locally."""
    root = (project_dir or find_project_root()).resolve()
    if shutil.which("docker") and _compose_up(root, detach):
        return
    console.print(
        "[yellow]Docker not found — starting apps natively (needs uv + node/pnpm).[/yellow]"
    )
    _native(root)


def _compose_up(root: Path, detach: bool) -> bool:
    cmd = ["docker", "compose", "up"] + (["-d"] if detach else [])
    try:
        subprocess.run(cmd, cwd=root, check=True)
        if detach:
            console.print("[green]✓[/green] Running — http://localhost:3000")
        return True
    except subprocess.CalledProcessError as exc:
        console.print(f"[red]docker compose failed ({exc.returncode})[/red]")
        raise typer.Exit(exc.returncode or 1) from None


def _native(root: Path) -> None:
    uv, pnpm, npm = shutil.which("uv"), shutil.which("pnpm"), shutil.which("npm")
    if not uv or not (pnpm or npm):
        console.print(
            "[red]Need `uv` and `pnpm`/`npm` for native dev, or Docker for compose.[/red]"
        )
        raise typer.Exit(1)
    agent = subprocess.Popen(
        [
            uv,
            "run",
            "--directory",
            str(root / "apps/agent"),
            "uvicorn",
            "agent.main:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8123",
            "--reload",
        ],
        cwd=root,
    )
    pm = pnpm or npm
    web = subprocess.Popen([pm, "--dir", str(root / "apps/web"), "dev"], cwd=root, shell=True)
    console.print("agent → http://127.0.0.1:8123  ·  web → http://localhost:3000  (Ctrl+C to stop)")
    try:
        web.wait()
    except KeyboardInterrupt:
        pass
    finally:
        for proc in (web, agent):
            proc.send_signal(signal.SIGINT)
        web.wait(timeout=10)
        agent.wait(timeout=10)
