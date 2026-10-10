"""Minimal provider-agnostic LLM completion used by `--assist` / `--ai` flows.

Supports Anthropic, OpenAI and Gemini out of the user's own env keys — no heavy
SDK deps. Returns plain text; callers handle parsing.
"""

from __future__ import annotations

import os

import httpx

_TIMEOUT = 60


def available_provider() -> str | None:
    for env in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        if os.getenv(env):
            return env
    return None


def complete(system: str, user: str, model: str | None = None) -> str:
    """One-shot completion. Picks a provider from env keys, Anthropic first."""
    if key := os.getenv("ANTHROPIC_API_KEY"):
        return _anthropic(system, user, key, model or "claude-sonnet-4-5")
    if key := os.getenv("OPENAI_API_KEY"):
        return _openai(system, user, key, model or "gpt-4o")
    key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if key:
        return _gemini(system, user, key, model or "gemini-2.5-flash")
    raise RuntimeError(
        "No LLM key found — set ANTHROPIC_API_KEY, OPENAI_API_KEY or GEMINI_API_KEY."
    )


def _anthropic(system: str, user: str, key: str, model: str) -> str:
    resp = httpx.post(
        "https://api.anthropic.com/v1/messages",
        headers={"x-api-key": key, "anthropic-version": "2023-06-01"},
        json={
            "model": model,
            "max_tokens": 2048,
            "system": system,
            "messages": [{"role": "user", "content": user}],
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return "".join(b["text"] for b in resp.json()["content"] if b["type"] == "text")


def _openai(system: str, user: str, key: str, model: str) -> str:
    resp = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={"Authorization": f"Bearer {key}"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["choices"][0]["message"]["content"]


def _gemini(system: str, user: str, key: str, model: str) -> str:
    resp = httpx.post(
        f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
        headers={"x-goog-api-key": key},
        json={
            "system_instruction": {"parts": [{"text": system}]},
            "contents": [{"parts": [{"text": user}]}],
        },
        timeout=_TIMEOUT,
    )
    resp.raise_for_status()
    return resp.json()["candidates"][0]["content"]["parts"][0]["text"]
