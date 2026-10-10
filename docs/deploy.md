# Deploying

## Railway

`myg deploy` runs `railway up` when the CLI is present; otherwise your generated
`RAILWAY.md` walks the dashboard flow — two services (`apps/web`, `apps/agent`),
a Postgres plugin or your Neon URL, env vars per service, public domain on web.

## Docker anywhere

Every generated app builds self-contained images:

```bash
docker build -f apps/agent/Dockerfile -t my-agent .
docker build -f apps/web/Dockerfile -t my-web .
```

Point `AGENT_URL` at the agent's public URL on web, `DATABASE_URL` + LLM key on
the agent, done.

## Notes on the Neon claimable DB

`myg db` provisions Neon Postgres **without an account** — it expires in 72h
unless you open the printed `claim_url` and sign in. For production, claim it
(or use Railway's Postgres / any `DATABASE_URL`).
