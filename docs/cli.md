# CLI reference

## `myg init`

Scaffold a new app.

| Flag | Purpose |
| --- | --- |
| `--yes` / `--defaults` | Skip wizard, use flags + defaults |
| `--assist` | LLM fills config from your description |
| `--github-style <url>` | Extract theme from a GitHub repo's CSS |
| `--pattern` | `react` / `plan_execute` / `supervisor` / `swarm` / `rag` / `hitl` / `evaluator_optimizer` |
| `--model` | `provider:model` e.g. `openai:gpt-4o` |
| `--system-prompt`, `--subagents` | Agent config |
| `--db` | `neon` / `postgres` / `sqlite` |
| `--gateway` | `off` / `local` / `konnect` |
| `--ui-style`, `--primary-color`, `--secondary-color` | Theme |
| `--output-dir`, `--template`, `--no-provision`, `--dry-run` | Output control |

## `myg configure`

Edit `myg.toml` on an existing app and re-render template files.

```bash
myg configure --set agent.pattern=swarm
myg configure --get agent.model
myg configure --ai                      # reconfigure by chatting
myg configure --github-style <url>      # re-theme from a repo
myg configure --no-render               # toml only
```

## `myg prompt "<instruction>"`

Agentic edits to your app — "add a tool", "make the UI sexier", "add auth".
Default backend is the Claude Agent SDK (`pip install 'myg[agent]'` + Anthropic
key/sub). `--backend devin` opens an async Devin session instead (`DEVIN_API_KEY`).

## `myg dev` / `myg doctor`

`dev` runs `docker compose up` (or native uv + node fallback). `doctor` checks
docker/node/uv/keys/ports/network.

## `myg db` / `myg db-claim`

Provisions instant Neon Postgres → writes `DATABASE_URL` to `.env` → prints the
claim URL (72h expiry otherwise). `db-claim` reprints it.

## `myg deploy` / `myg update` / `myg templates`

`deploy` runs `railway up` or prints the guided steps (see `RAILWAY.md` in your
app). `update` applies template upgrades via cruft. `templates` lists available
templates for `--template`.

## `myg eject`

Cuts the project loose from the template — deletes `.cruft.json` so `myg update`
and `myg configure` re-renders can never overwrite your files again. `myg.toml`
stays (the agent loads it at runtime), and `db`/`dev`/`deploy`/`prompt` keep
working. One-way by design — `git init` first if you want a rollback point.
