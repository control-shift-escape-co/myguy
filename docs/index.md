# myg

**your guy for agent apps.**

`myg init` scaffolds a single-page agent app:

- **apps/web** — Next.js + [CopilotKit](https://copilotkit.ai) chat UI speaking [AG-UI](https://github.com/ag-ui-protocol/ag-ui)
- **apps/agent** — FastAPI + [LangGraph](https://langchain-ai.github.io/langgraph/) backend, pick from four agentic patterns
- **threads** — Postgres persistence via Neon (instant, no account), Docker, or SQLite
- **gateway** — optional Kong AI Gateway (local decK or Konnect) for LLM auth/limits/observability
- **deploy** — `docker compose up` locally, or Railway with `myg deploy`

## Credentials you need

| Credential | When |
| --- | --- |
| `OPENAI_API_KEY` / `ANTHROPIC_API_KEY` / `GEMINI_API_KEY` | Always (one, matching your model) |
| `KONNECT_TOKEN` | Only `gateway=konnect` |
| `RAILWAY_TOKEN` | Only `myg deploy` |
| `ANTHROPIC_API_KEY` | Only `myg prompt` |

Everything else — database, runtime, gateway — is provisioned or containerized for you.

## Install

```bash
uvx myg init          # uv — recommended
pipx run myg init     # pipx
pip install myg       # pip
npm create myg        # npm (delegates to uvx/pipx)
```
