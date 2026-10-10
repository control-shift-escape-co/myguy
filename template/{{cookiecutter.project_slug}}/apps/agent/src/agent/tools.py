"""Starter tools shared by all patterns. Replace the mocks with real APIs."""

from __future__ import annotations

from datetime import datetime, timezone

from langchain_core.tools import tool


@tool
def get_current_time() -> str:
    """Return the current UTC time (ISO 8601)."""
    return datetime.now(timezone.utc).isoformat()


@tool
def get_weather(city: str) -> str:
    """Get the weather for a city. MOCK — wire up a real weather API here."""
    return f"Sunny, 24°C in {city} (mock data — plug in a real provider in tools.py)"


@tool
def web_search(query: str) -> str:
    """Search the web. MOCK — wire up Tavily/Serper/Bing here."""
    return f"[mock search results for: {query}] — replace with a real search API in tools.py"


DEFAULT_TOOLS = [get_current_time, get_weather, web_search]
