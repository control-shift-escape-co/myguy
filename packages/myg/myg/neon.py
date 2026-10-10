"""Instant Postgres via Neon's claimable database API — no account required.

POST https://neon.new/api/v1/database -> connection string + claim URL.
The DB works immediately and expires in 72h unless the user claims it at the
printed URL (sign-in only, no card). See https://neon.com/docs/reference/claimable-postgres
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import httpx
from rich.console import Console

NEON_API = "https://neon.new/api/v1"
console = Console()


@dataclass
class NeonDatabase:
    id: str
    connection_string: str
    claim_url: str
    expires_at: str


def provision(ref: str = "myg") -> NeonDatabase:
    """Create an instant, unauthenticated Neon Postgres database."""
    resp = httpx.post(f"{NEON_API}/database", json={"ref": ref}, timeout=30)
    resp.raise_for_status()
    data = resp.json()
    return NeonDatabase(
        id=data["id"],
        connection_string=data["connection_string"],
        claim_url=data.get("claim_url", ""),
        expires_at=data.get("expires_at", ""),
    )


def status(db_id: str) -> dict:
    resp = httpx.get(f"{NEON_API}/database/{db_id}", timeout=30)
    resp.raise_for_status()
    return resp.json()


def write_database_url(project_dir: Path, url: str) -> Path:
    """Write DATABASE_URL into the project's .env (create from .env.example if needed)."""
    env_file = project_dir / ".env"
    if not env_file.exists():
        example = project_dir / ".env.example"
        env_file.write_text(
            example.read_text(encoding="utf-8") if example.exists() else "", encoding="utf-8"
        )
    lines = env_file.read_text(encoding="utf-8").splitlines()
    for i, line in enumerate(lines):
        if line.startswith("DATABASE_URL="):
            lines[i] = f"DATABASE_URL={url}"
            break
    else:
        lines.append(f"DATABASE_URL={url}")
    env_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return env_file
