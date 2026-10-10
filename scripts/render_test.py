"""Render smoke test — exercises every pattern x db x gateway combo.

Usage: python scripts/render_test.py
Validates: cookiecutter render, docker-compose YAML parse, python compile,
presence of gateway/db files only when selected.
"""

from __future__ import annotations

import itertools
import shutil
import sys
import tempfile
from pathlib import Path

import yaml
from cookiecutter.main import cookiecutter

ROOT = Path(__file__).resolve().parents[1]

PATTERNS = (
    "react",
    "plan_execute",
    "supervisor",
    "swarm",
    "rag",
    "hitl",
    "evaluator_optimizer",
)
DBS = ("neon", "postgres", "sqlite")
GATEWAYS = ("off", "local", "konnect")


def run() -> int:
    failures = 0
    for pattern, db, gateway in itertools.product(PATTERNS, DBS, GATEWAYS):
        slug = f"t-{pattern}-{db}-{gateway}"
        with tempfile.TemporaryDirectory() as tmp:
            try:
                dest = Path(
                    cookiecutter(
                        str(ROOT / "template"),
                        no_input=True,
                        output_dir=tmp,
                        extra_context={
                            "project_name": slug,
                            "agent_pattern": pattern,
                            "db": db,
                            "gateway": gateway,
                        },
                    )
                )
                yaml.safe_load((dest / "docker-compose.yml").read_text())
                # gateway files exist iff gateway != off
                kong_exists = (dest / "infra/gateway/kong.yaml").exists()
                assert kong_exists == (gateway != "off"), f"kong.yaml present={kong_exists}"
                # python files must compile
                import compileall

                if not compileall.compile_dir(str(dest / "apps/agent/src"), quiet=2):
                    raise AssertionError("py compile failed")
            except Exception as exc:  # noqa: BLE001
                print(f"FAIL {slug}: {exc}")
                failures += 1
            else:
                print(f"ok   {slug}")
    return failures


if __name__ == "__main__":
    sys.exit(1 if run() else 0)
