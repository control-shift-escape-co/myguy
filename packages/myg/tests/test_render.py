"""Template rendering — a few representative combos, not the full matrix
(scripts/render_test.py covers all of them in CI)."""

from __future__ import annotations

from pathlib import Path

import pytest
from myg.context import MygContext
from myg.render import create_project


def render(tmp_path: Path, **kwargs) -> Path:
    ctx = MygContext(project_name="test app", **kwargs)
    return create_project(ctx.cookiecutter_context(), tmp_path)


def test_default_render(tmp_path):
    dest = render(tmp_path)
    assert (dest / "myg.toml").exists()
    assert (dest / "docker-compose.yml").exists()
    assert (dest / "apps/web/package.json").exists()
    assert (dest / "apps/agent/src/agent/main.py").exists()
    # default gateway=off → no infra dir; default pattern=react → no knowledge dir
    assert not (dest / "infra").exists()
    assert not (dest / "knowledge").exists()
    assert (dest / ".cruft.json").exists()  # local renders still link for `myg update`


def test_rag_pattern_ships_knowledge(tmp_path):
    dest = render(tmp_path, agent_pattern="rag")
    assert (dest / "knowledge" / "about.md").exists()
    dockerfile = (dest / "apps/agent/Dockerfile").read_text()
    assert "COPY knowledge ./knowledge" in dockerfile


def test_gateway_local_ships_kong(tmp_path):
    dest = render(tmp_path, gateway="local")
    assert (dest / "infra/gateway/kong.yaml").exists()
    assert "kong" in (dest / "docker-compose.yml").read_text()


def test_gateway_konnect_ships_script(tmp_path):
    dest = render(tmp_path, gateway="konnect")
    assert (dest / "infra/konnect/setup-konnect.sh").exists()
    assert "control-planes" in (dest / "infra/konnect/setup-konnect.sh").read_text()


@pytest.mark.parametrize(
    "pattern",
    ["react", "plan_execute", "supervisor", "swarm", "rag", "hitl", "evaluator_optimizer"],
)
def test_every_pattern_renders(tmp_path, pattern):
    dest = render(tmp_path, agent_pattern=pattern)
    assert (dest / "myg.toml").exists()
