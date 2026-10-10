# AI Gateway (Kong)

`gateway` in myg.toml controls whether LLM traffic flows through Kong.

## `local` (default when enabled)

`docker-compose.yml` adds a db-less Kong container loading
`infra/gateway/kong.yaml` (decK). The `ai-proxy` plugin fronts `/llm` with:

- upstream auth to your provider — `LLM_API_KEY` from `.env` is substituted
  into the config at container start (`__LLM_API_KEY__` placeholder; Kong's
  declarative loader doesn't read env vars), so no key lives in `kong.yaml`
- per-minute rate limiting
- request stats logging

The provider/model are baked from `[agent].model` in `myg.toml` at render time
(provider-specific auth is handled: `x-api-key` for Anthropic, `?key=` for
Gemini, `Authorization: Bearer` otherwise). `myg configure --set agent.model=...`
re-renders it.

The agent's `LLM_BASE_URL` points at `http://kong:8000/llm` and speaks the
OpenAI wire format regardless of the upstream provider — swap providers in
`myg.toml` without touching agent code.

## `konnect`

Kong Konnect = the managed control plane. It needs a **personal access token**
in `KONNECT_TOKEN` — there's no zero-touch path here (a human account is
required upstream).

```bash
export KONNECT_TOKEN=...
bash infra/konnect/setup-konnect.sh
```

The script automates everything the API allows:

1. creates an AI Gateway control plane
2. issues a data-plane client certificate → `infra/konnect/dp-{cert,key}.pem`
   (git-ignored)
3. syncs `infra/gateway/kong.yaml` to the control plane — automatically when
   [`deck`](https://docs.konghq.com/deck/) is installed, otherwise it prints
   the exact command
4. prints a ready-to-run data-plane `docker run` (certs inline, no copy-paste)

Point the agent at the data plane with `LLM_BASE_URL=http://localhost:8000/llm`.

## `off`

Agent talks to the provider directly using its env key. `LLM_BASE_URL` can
still reroute the client to any OpenAI-compatible endpoint.
