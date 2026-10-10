# myg

Your guy for agent apps.

`myg init` scaffolds a production-shaped single-page agent app — Next.js + CopilotKit frontend, FastAPI + LangGraph backend (AG-UI), Postgres thread persistence, optional Kong AI Gateway — ready for `docker compose up` or a Railway deploy.

See the main repo for docs, contributing, and the full story: <https://github.com/control-shift-escape-co/myguy>

## Install

```bash
uvx myg init          # recommended — no install
pipx run myg init     # pipx
pip install myg       # classic
npm create myg        # npm folks — delegates to uvx/pipx
```

## Commands

| Command | What it does |
| --- | --- |
| `myg init` | Wizard → renders the template → optional instant Neon DB → next steps |
| `myg configure` | Edit `myg.toml` and re-render template files (`get`/`set`/`--ai`) |
| `myg prompt "…"` | Agentic edits to an existing app (Claude Agent SDK, or `--backend devin`) |
| `myg dev` | `docker compose up` — or runs both apps natively |
| `myg db` | Provisions an instant Neon Postgres + prints the claim URL |
| `myg deploy` | Deploys to Railway (CLI detected) or prints the guided steps |
| `myg doctor` | Checks docker/node/uv/keys/ports |
| `myg update` | Pulls template upgrades into your project (cruft) |
| `myg templates` | Lists built-in + community templates |

MIT licensed.
