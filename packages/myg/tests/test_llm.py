"""Provider detection + completion dispatch — httpx calls are mocked."""

from __future__ import annotations

import pytest
from myg import llm


@pytest.fixture(autouse=True)
def _clean_keys(monkeypatch):
    for k in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"):
        monkeypatch.delenv(k, raising=False)


def test_available_provider_priority(monkeypatch):
    assert llm.available_provider() is None
    monkeypatch.setenv("OPENAI_API_KEY", "x")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "x")
    assert llm.available_provider() == "ANTHROPIC_API_KEY"


def test_complete_no_key_raises():
    with pytest.raises(RuntimeError, match="No LLM key"):
        llm.complete("s", "u")


def test_complete_openai(monkeypatch):
    monkeypatch.setenv("OPENAI_API_KEY", "k")
    seen = {}

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "hi"}}]}

    def fake_post(url, **kwargs):
        seen["url"] = url
        return Resp()

    monkeypatch.setattr(llm.httpx, "post", fake_post)
    assert llm.complete("s", "u") == "hi"
    assert "openai.com" in seen["url"]


def test_complete_anthropic(monkeypatch):
    monkeypatch.setenv("ANTHROPIC_API_KEY", "k")
    seen = {}

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"content": [{"type": "text", "text": "hey"}]}

    def fake_post(url, **kwargs):
        seen["url"] = url
        return Resp()

    monkeypatch.setattr(llm.httpx, "post", fake_post)
    assert llm.complete("s", "u") == "hey"
    assert "anthropic.com" in seen["url"]
