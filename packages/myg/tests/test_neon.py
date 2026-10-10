"""DATABASE_URL handling — no live Neon calls here, just file behavior."""

from __future__ import annotations

from myg.neon import write_database_url

URL = "postgres://u:p@host/db?sslmode=require"


def test_creates_env_from_example(tmp_path):
    (tmp_path / ".env.example").write_text("OPENAI_API_KEY=\nDATABASE_URL=\n")
    env = write_database_url(tmp_path, URL)
    text = env.read_text()
    assert "OPENAI_API_KEY=" in text
    assert f"DATABASE_URL={URL}" in text


def test_replaces_existing_value(tmp_path):
    (tmp_path / ".env").write_text("DATABASE_URL=postgres://old\nFOO=1\n")
    write_database_url(tmp_path, URL)
    lines = (tmp_path / ".env").read_text().splitlines()
    assert lines == [f"DATABASE_URL={URL}", "FOO=1"]


def test_appends_when_missing(tmp_path):
    (tmp_path / ".env").write_text("FOO=1\n")
    write_database_url(tmp_path, URL)
    assert (tmp_path / ".env").read_text() == f"FOO=1\nDATABASE_URL={URL}\n"
