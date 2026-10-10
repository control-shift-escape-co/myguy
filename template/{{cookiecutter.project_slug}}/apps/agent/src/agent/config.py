"""Runtime config: reads myg.toml + environment into a single AgentConfig."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass(frozen=True)
class SubAgent:
    """A worker agent for supervisor/swarm patterns: name + its own system prompt."""

    name: str
    prompt: str


@dataclass(frozen=True)
class AgentConfig:
    app_name: str
    pattern: str  # react | plan_execute | supervisor | swarm
    model_provider: str
    model_name: str
    system_prompt: str
    subagents: tuple[SubAgent, ...]
    db_provider: str  # neon | postgres | sqlite
    database_url: str | None
    llm_base_url: str | None  # OpenAI-compatible endpoint when routing via the gateway


DEFAULT_SUBAGENTS = """researcher:Research the user's topic thoroughly and return key facts.
writer:Turn the gathered material into polished, well-structured prose."""


def _parse_subagents(raw: str) -> tuple[SubAgent, ...]:
    """Parse 'name:prompt' lines from myg.toml into SubAgent objects."""
    out = []
    for line in raw.strip().splitlines():
        name, _, prompt = line.partition(":")
        if name.strip() and prompt.strip():
            out.append(SubAgent(name=name.strip(), prompt=prompt.strip()))
    return tuple(out)


def _find_myg_toml() -> Path:
    if env := os.getenv("MYG_CONFIG"):
        return Path(env)
    for base in (Path.cwd(), *Path(__file__).resolve().parents):
        if (base / "myg.toml").exists():
            return base / "myg.toml"
    raise FileNotFoundError("myg.toml not found — set MYG_CONFIG or run from the project root.")


def load_config() -> AgentConfig:
    toml_path = _find_myg_toml()
    # .env always sits next to myg.toml — resolve relative to it, not cwd or
    # the caller frame (a bare load_dotenv() misses .env for installed wheels).
    load_dotenv(toml_path.parent / ".env")
    data = tomllib.loads(toml_path.read_text(encoding="utf-8"))
    model = data["agent"]["model"]
    provider, _, model_name = model.partition(":")
{% if cookiecutter.gateway != "off" %}
    # Gateway mode: all providers normalize to OpenAI-format through Kong.
    base_url = os.getenv("LLM_BASE_URL", "http://localhost:8000/llm")
    provider = "openai"
{% else %}
    base_url = os.getenv("LLM_BASE_URL") or None
{% endif %}
    return AgentConfig(
        app_name=data["project"]["name"],
        pattern=data["agent"]["pattern"],
        model_provider=provider or "openai",
        model_name=model_name or "gpt-4o",
        system_prompt=data["agent"].get("system_prompt", "").strip(),
        subagents=_parse_subagents(data["agent"].get("subagents", "") or DEFAULT_SUBAGENTS),
        db_provider=data["db"].get("provider", "sqlite"),
        database_url=os.getenv("DATABASE_URL") or None,
        llm_base_url=base_url,
    )
