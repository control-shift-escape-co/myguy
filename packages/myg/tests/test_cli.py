"""CLI surface — typer CliRunner, no network-dependent paths."""

from __future__ import annotations

from myg.cli import app
from myg.context import MygContext
from myg.render import create_project
from typer.testing import CliRunner

runner = CliRunner()


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "myg" in result.output


def test_help_lists_commands():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for cmd in ("init", "configure", "db", "dev", "deploy", "doctor", "update", "eject"):
        assert cmd in result.output


def test_templates_without_network():
    result = runner.invoke(app, ["templates"])
    assert result.exit_code == 0
    assert "react" in result.output


def test_eject(tmp_path):
    dest = create_project(MygContext(project_name="eject me").cookiecutter_context(), tmp_path)
    assert (dest / ".cruft.json").exists()

    result = runner.invoke(app, ["eject", "--dir", str(dest), "--yes"])
    assert result.exit_code == 0, result.output
    assert not (dest / ".cruft.json").exists()

    again = runner.invoke(app, ["eject", "--dir", str(dest), "--yes"])
    assert again.exit_code == 0
    assert "Already ejected" in again.output


def test_doctor_uses_dir_flag(tmp_path):
    dest = create_project(MygContext(project_name="doc test").cookiecutter_context(), tmp_path)
    result = runner.invoke(app, ["doctor", "--dir", str(dest)], env={"ANTHROPIC_API_KEY": "x"})
    # exit code depends on the host env (ports/network); the --dir flag must be honored
    assert "project detected" in result.output


def test_configure_get(tmp_path):
    dest = create_project(
        MygContext(project_name="cfg test", model="gemini:gemini-2.5-flash").cookiecutter_context(),
        tmp_path,
    )
    result = runner.invoke(app, ["configure", "--dir", str(dest), "--get", "agent.model"])
    assert result.exit_code == 0
    assert "gemini:gemini-2.5-flash" in result.output
