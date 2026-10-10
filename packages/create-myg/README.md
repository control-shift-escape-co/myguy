# create-myg

```bash
npm create myg
```

Scaffolds a single-page agent app — Next.js + CopilotKit frontend, FastAPI + LangGraph backend (AG-UI), Postgres threads, optional Kong AI Gateway.

This is a thin wrapper that delegates to the Python [`myg`](https://pypi.org/project/myg/) CLI via `uvx`/`pipx`. Requires one of: `uv`, `pipx`, or `myg` on PATH (`pip install myg`).

Docs + source: <https://github.com/control-shift-escape-co/myguy> — MIT.
