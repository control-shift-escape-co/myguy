"""MygContext + find_project_root — the config single-source-of-truth."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from myg.context import MygContext, find_project_root, slugify

REPO_ROOT = Path(__file__).resolve().parents[3]


def test_slugify():
    assert slugify("My Cool App") == "my-cool-app"
    assert slugify("  weird__name!! ") == "weird-name"
    assert slugify("!!!") == "my-agent-app"


def test_context_covers_cookiecutter_vars():
    """Every cookiecutter.json variable (except derived/private) is emitted."""
    spec = json.loads((REPO_ROOT / "template" / "cookiecutter.json").read_text())
    expected = {k for k in spec if not k.startswith("_")} - {"project_slug"}
    ctx = MygContext().cookiecutter_context()
    assert expected <= set(ctx)


def test_myg_toml_round_trip(tmp_path):
    ctx = MygContext(project_name="Round Trip", agent_pattern="swarm", db="sqlite")
    path = tmp_path / "myg.toml"
    ctx.write_myg_toml(path)
    loaded = MygContext.from_myg_toml(path)
    assert loaded.project_name == "Round Trip"
    assert loaded.agent_pattern == "swarm"
    assert loaded.db == "sqlite"
    assert loaded.model == ctx.model


def test_find_project_root(tmp_path, tmp_path_factory):
    (tmp_path / "myg.toml").write_text("[project]\nname='x'\n")
    nested = tmp_path / "a" / "b"
    nested.mkdir(parents=True)
    assert find_project_root(nested) == tmp_path
    elsewhere = tmp_path_factory.mktemp("no-mygtoml")
    with pytest.raises(FileNotFoundError):
        find_project_root(elsewhere)
