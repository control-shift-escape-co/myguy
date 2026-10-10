# Deploy to Railway

This repo ships two services (web + agent) plus optional Postgres/Kong. Two
minutes of dashboard clicking gets it live — or `railway up` if you have the CLI.

## Steps

1. **Push this project to GitHub.**
2. **railway.app → New Project → Deploy from GitHub repo.**
3. **Create two services from the same repo**, each with its own root directory:
   - `web` — root dir `apps/web` (Dockerfile auto-detected)
   - `agent` — root dir `apps/agent` (Dockerfile auto-detected — note the
     Dockerfile expects the repo root as build context; set **Build Context**
     to the repo root in the service settings)
4. **Postgres:** add a Railway Postgres plugin and reference `DATABASE_URL` on
   the agent service — or reuse a Neon URL.
{% if cookiecutter.db == "neon" -%}
   This project was scaffolded with Neon — paste `DATABASE_URL` from your
   `.env` into the agent service variables.
{%- endif %}
5. **Env vars:**
   - `agent`: `OPENAI_API_KEY` (or your provider key){% if cookiecutter.gateway != "off" %}, `LLM_BASE_URL` pointing at your gateway{% endif %}
   - `web`: `AGENT_URL=https://<agent-service>.up.railway.app/agent`,
     `NEXT_PUBLIC_APP_NAME={{ cookiecutter.project_name }}`
6. **Public networking:** enable a public domain on both services; the web
   service is your entry point.

## CLI path

```bash
npm i -g @railway/cli
railway login
railway init   # inside this repo — creates the project
railway up
```
