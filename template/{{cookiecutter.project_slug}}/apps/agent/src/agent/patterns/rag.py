"""Agentic RAG — a ReAct agent with a `search_knowledge_base` tool.

The retriever is deliberately dependency-free: markdown/text files in the
project's `knowledge/` directory are chunked on blank lines and scored by
weighted term overlap. Swap `_retrieve` for a real vector store (pgvector is a
natural fit — you already have Postgres) when the corpus outgrows keyword
matching.
"""

from __future__ import annotations

import math
import re
from collections import Counter
from pathlib import Path

from langchain.agents import create_agent
from langchain_core.tools import tool

from agent.config import AgentConfig, _find_myg_toml
from agent.model import build_model
from agent.tools import DEFAULT_TOOLS

_TOP_K = 4
_TOKEN = re.compile(r"[a-z0-9]+")


def _knowledge_dir() -> Path:
    """knowledge/ sits next to myg.toml — in the image at /app, on disk at root."""
    try:
        return _find_myg_toml().parent / "knowledge"
    except FileNotFoundError:
        return Path("knowledge")


def _chunks() -> list[str]:
    out: list[str] = []
    root = _knowledge_dir()
    for path in sorted(root.glob("**/*.md")) + sorted(root.glob("**/*.txt")):
        for block in path.read_text(encoding="utf-8", errors="replace").split("\n\n"):
            block = block.strip()
            if len(block) > 40:
                out.append(f"[{path.name}] {block}")
    return out


def _retrieve(query: str) -> list[str]:
    """BM25-lite: score chunks by tf-idf-weighted term overlap with the query."""
    chunks = _chunks()
    if not chunks:
        return []
    terms = _TOKEN.findall(query.lower())
    if not terms:
        return []
    tf = [Counter(_TOKEN.findall(c)) for c in chunks]
    df = Counter(t for counts in tf for t in set(counts) & set(terms))
    n = len(chunks)

    def score(i: int) -> float:
        return sum(
            tf[i][t] * math.log((n + 1) / (df[t] + 0.5)) for t in set(terms) if t in df
        ) / math.sqrt(len(chunks[i].split()) + 1)

    ranked = sorted(range(n), key=score, reverse=True)
    return [chunks[i] for i in ranked[:_TOP_K] if score(i) > 0]


def build_graph(cfg: AgentConfig, checkpointer):
    @tool
    def search_knowledge_base(query: str) -> str:
        """Search the app's local knowledge base (knowledge/*.md). Use for
        questions about this app's domain before answering from memory."""
        hits = _retrieve(query)
        return "\n\n".join(hits) if hits else "No relevant documents found in knowledge/."

    prompt = (
        f"{cfg.system_prompt}\n\n"
        "You have a `search_knowledge_base` tool over the app's documents — call "
        "it whenever the answer might live in project knowledge, and cite what "
        "you used."
    )
    return create_agent(
        model=build_model(cfg),
        tools=[search_knowledge_base, *DEFAULT_TOOLS],
        system_prompt=prompt,
        checkpointer=checkpointer,
    )
