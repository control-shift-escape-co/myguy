# The generated app

```
my-app/
├── myg.toml                 # config single-source — `myg configure` edits it
├── .env(.example)           # credentials
├── docker-compose.yml       # web + agent (+ db / kong, per config)
├── Makefile                 # lint / fmt / check / up / down
├── RAILWAY.md               # deploy guide
├── apps/
│   ├── web/                 # Next.js 15 + CopilotKit
│   │   ├── src/app/api/copilotkit/route.ts   # CopilotRuntime → HttpAgent → backend
│   │   └── src/app/globals.css             # theme tokens + CopilotKit vars
│   └── agent/               # FastAPI + LangGraph
│       └── src/agent/
│           ├── config.py         # myg.toml + env → AgentConfig
│           ├── model.py          # init_chat_model (gateway-aware base_url)
│           ├── checkpoints.py    # Postgres / SQLite thread saver
│           ├── tools.py          # starter tools — replace the mocks
│           ├── patterns/         # react, plan_execute, supervisor, swarm,
│           │                     # rag, hitl, evaluator_optimizer
│           └── main.py           # mounts AG-UI endpoint at /agent
├── knowledge/                # *.md|*.txt the rag pattern retrieves (rag only)
└── infra/
    ├── gateway/kong.yaml    # decK ai-proxy config (gateway=local)
    └── konnect/             # konnect provisioning script (gateway=konnect)
```

## Request flow

```
browser → Next.js (CopilotKit UI)
        → /api/copilotkit (CopilotRuntime)
        → HttpAgent → FastAPI /agent (AG-UI SSE)
        → LangGraph pattern → tools/LLM (via Kong when gateway=on)
        → PostgresSaver → threads
```

## myg.toml

```toml
[agent]   pattern, model, system_prompt, subagents
[ui]      style, primary_color, secondary_color
[db]      provider (+ neon claim metadata)
[gateway] mode
```

`myg configure` updates it and re-renders template-owned files. `.cruft.json`
tracks the template version for `myg update`. `myg eject` removes that link
when you're ready to own every line.

## Community templates

`myg init --template <git-url-or-path>` renders any cookiecutter template that
follows the myg contract:

- a `cookiecutter.json` exposing the same variables (`project_name`,
  `agent_pattern`, `model`, `subagents`, `ui_style`, `primary_color`,
  `secondary_color`, `db`, `gateway`, `description`, `system_prompt`)
- the generated tree keeps `myg.toml` at the root so `configure`/`db`/`dev`/
  `doctor`/`deploy` keep working
- a `template/` subdir layout gets cruft-powered `myg update` for free

To list yours, send a PR adding an entry to
[`template/templates-registry.json`](https://github.com/control-shift-escape-co/myguy/blob/master/template/templates-registry.json):

```json
{ "name": "your-template", "source": "https://github.com/you/your-template", "notes": "what it does differently" }
```

It shows up under `myg templates --community` as soon as the PR lands.
