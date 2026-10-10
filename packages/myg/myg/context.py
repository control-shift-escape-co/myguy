"""The single source of truth shared by `myg init`, `myg configure` and the template.

A :class:`MygContext` maps 1:1 onto ``cookiecutter.json`` variables and onto the
``myg.toml`` file inside every generated project. Keep field names identical to
the cookiecutter variables so ``cookiecutter_context`` stays a plain dump.
"""

from __future__ import annotations

import re
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import tomli_w

PATTERNS = (
    "react",
    "plan_execute",
    "supervisor",
    "swarm",
    "rag",
    "hitl",
    "evaluator_optimizer",
)
DBS = ("neon", "postgres", "sqlite")
GATEWAYS = ("off", "local", "konnect")
UI_STYLES = ("default", "terminal", "brutalist")
MODEL_SUGGESTIONS = (
    "openai:gpt-4o",
    "openai:gpt-4o-mini",
    "anthropic:claude-sonnet-4-5",
    "anthropic:claude-haiku-4-5",
    "gemini:gemini-2.5-flash",
)

DEFAULT_SUBAGENTS = (
    "researcher:Research the user's topic thoroughly and return key facts.",
    "writer:Turn the gathered material into polished, well-structured prose.",
)


def slugify(name: str) -> str:
    """'My Cool App' -> 'my-cool-app'."""
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", name.strip()).strip("-").lower()
    return slug or "my-agent-app"


@dataclass
class MygContext:
    """Everything the template needs. Field names == cookiecutter.json keys."""

    project_name: str = "my-agent-app"
    description: str = "A single-page agent app scaffolded by myg."
    agent_pattern: str = "react"
    system_prompt: str = "You are a helpful assistant. Be concise and genuinely useful."
    model: str = "openai:gpt-4o"
    subagents: str = "\n".join(DEFAULT_SUBAGENTS)
    ui_style: str = "default"
    primary_color: str = "#1d4ed8"
    secondary_color: str = "#f59e0b"
    db: str = "neon"
    gateway: str = "off"
    _extra: dict[str, Any] = field(default_factory=dict)

    @property
    def project_slug(self) -> str:
        return slugify(self.project_name)

    @property
    def model_provider(self) -> str:
        return self.model.split(":", 1)[0]

    @property
    def model_name(self) -> str:
        return self.model.split(":", 1)[-1]

    def cookiecutter_context(self) -> dict[str, Any]:
        return {
            "project_name": self.project_name,
            "project_slug": self.project_slug,
            "description": self.description,
            "agent_pattern": self.agent_pattern,
            "system_prompt": self.system_prompt,
            "model": self.model,
            "subagents": self.subagents,
            "ui_style": self.ui_style,
            "primary_color": self.primary_color,
            "secondary_color": self.secondary_color,
            "db": self.db,
            "gateway": self.gateway,
            **self._extra,
        }

    def write_myg_toml(self, path: Path, **extra: Any) -> None:
        """Persist context as myg.toml inside the generated project."""
        doc: dict[str, Any] = {
            "project": {"name": self.project_name, "description": self.description},
            "agent": {
                "pattern": self.agent_pattern,
                "system_prompt": self.system_prompt,
                "model": self.model,
                "subagents": self.subagents,
            },
            "ui": {
                "style": self.ui_style,
                "primary_color": self.primary_color,
                "secondary_color": self.secondary_color,
            },
            "db": {"provider": self.db},
            "gateway": {"mode": self.gateway},
        }
        for section, values in extra.items():
            doc.setdefault(section, {}).update(values)
        path.write_text(tomli_w.dumps(doc), encoding="utf-8")

    @classmethod
    def from_myg_toml(cls, path: Path) -> MygContext:
        data = tomllib.loads(path.read_text(encoding="utf-8"))
        return cls(
            project_name=data["project"]["name"],
            description=data["project"].get("description", ""),
            agent_pattern=data["agent"]["pattern"],
            system_prompt=data["agent"].get("system_prompt", ""),
            model=data["agent"].get("model", "openai:gpt-4o"),
            subagents=data["agent"].get("subagents", ""),
            ui_style=data["ui"].get("style", "default"),
            primary_color=data["ui"].get("primary_color", "#1d4ed8"),
            secondary_color=data["ui"].get("secondary_color", "#f59e0b"),
            db=data["db"].get("provider", "neon"),
            gateway=data["gateway"].get("mode", "off"),
        )


def find_project_root(start: Path | None = None) -> Path:
    """Walk upwards until a myg.toml is found — the generated project root."""
    here = (start or Path.cwd()).resolve()
    for candidate in (here, *here.parents):
        if (candidate / "myg.toml").exists():
            return candidate
    raise FileNotFoundError("No myg.toml found — run this inside a generated project.")
