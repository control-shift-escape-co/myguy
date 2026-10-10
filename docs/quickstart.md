# Quickstart

```bash
uvx myg init
```

The wizard asks for: project name, agent pattern, system prompt, model,
subagents (supervisor/swarm only), UI style + colors, database, gateway.

Non-interactive:

```bash
myg init my-app --yes --pattern supervisor --model openai:gpt-4o --db neon --gateway local
```

Other modes:

- `--assist` — describe the app in words, an LLM fills the config
- `--github-style https://github.com/org/site` — extracts a site's colors/vibe
- `--dry-run` — print the resolved config, render nothing
- `--template <git-url>` — render a community template

After init:

```bash
cd my-app
cp .env.example .env   # add your LLM key
myg dev                # or: docker compose up
```

Open <http://localhost:3000>. The agent's AG-UI endpoint is `http://localhost:8123/agent`.

If you picked `db=neon`, the claim URL printed at init keeps the DB alive past
its 72-hour expiry — open it, sign in, done.
