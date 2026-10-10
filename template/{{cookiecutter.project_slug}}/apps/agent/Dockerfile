# Build context: project ROOT (so myg.toml is reachable).
#   docker build -f apps/agent/Dockerfile .
FROM python:3.12-slim

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY myg.toml ./myg.toml
COPY apps/agent/pyproject.toml ./pyproject.toml
COPY apps/agent/src ./src
{% if cookiecutter.agent_pattern == "rag" -%}
COPY knowledge ./knowledge
{% endif -%}

RUN uv pip install --system --no-cache .

EXPOSE 8123
CMD ["uvicorn", "agent.main:app", "--host", "0.0.0.0", "--port", "8123"]
