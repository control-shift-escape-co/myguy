"""Template rendering: cruft for remote templates, cookiecutter for local trees.

Local paths render from the working tree (dev checkouts need uncommitted
files). Remote URLs go through cruft so `.cruft.json` lands in the project and
`myg update` can pull template upgrades later.
"""

from __future__ import annotations

import contextlib
import json
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from cookiecutter.main import cookiecutter
from cruft import create as cruft_create

DEFAULT_TEMPLATE = "https://github.com/control-shift-escape-co/myguy"
TEMPLATE_DIR = "template"


def local_template_root() -> Path | None:
    """Repo root containing template/ in a source checkout, else None."""
    for parent in Path(__file__).resolve().parents:
        if (parent / TEMPLATE_DIR / "cookiecutter.json").exists():
            return parent
    return None


def create_project(
    context: dict[str, Any],
    output_dir: Path,
    template: str | None = None,
) -> Path:
    """Render the template into output_dir/<project_slug>."""
    source = template or _default_template()
    if _is_remote(source):
        cruft_create(
            source,
            output_dir=output_dir,
            extra_context=context,
            directory=TEMPLATE_DIR,
            no_input=True,
            overwrite_if_exists=True,
        )
        return output_dir / context["project_slug"]
    dest = _render_local(source, context, output_dir)
    _write_cruft_json(Path(dest), source, context)
    return Path(dest)


def rerender(project_dir: Path, context: dict[str, Any], template: str | None = None) -> None:
    """Re-render template files in place with new values (template-owned files only)."""
    source = template or _default_template()
    with tempfile.TemporaryDirectory() as tmp:
        if _is_remote(source):
            rendered = cookiecutter(
                source,
                no_input=True,
                extra_context=context,
                output_dir=tmp,
                directory=TEMPLATE_DIR,
            )
        else:
            rendered = _render_local(source, context, Path(tmp))
        shutil.copytree(rendered, project_dir, dirs_exist_ok=True)


def _render_local(source: str, context: dict[str, Any], output_dir: Path) -> str:
    template_dir = Path(source)
    if (template_dir / TEMPLATE_DIR / "cookiecutter.json").exists():
        template_dir = template_dir / TEMPLATE_DIR
    return cookiecutter(
        str(template_dir),
        no_input=True,
        extra_context=context,
        output_dir=str(output_dir),
        overwrite_if_exists=True,
    )


def _write_cruft_json(project_dir: Path, source: str, context: dict[str, Any]) -> None:
    """Emit .cruft.json so `myg update` works on locally-rendered projects too."""
    template_ref = source if _is_remote(source) else DEFAULT_TEMPLATE
    commit = ""
    with contextlib.suppress(Exception):
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=source if not _is_remote(source) else project_dir,
            capture_output=True,
            text=True,
            timeout=10,
        ).stdout.strip()
    (project_dir / ".cruft.json").write_text(
        json.dumps(
            {
                "template": template_ref,
                "commit": commit,
                "checkout": None,
                "context": {"cookiecutter": context},
                "directory": TEMPLATE_DIR,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


def _is_remote(source: str) -> bool:
    return source.startswith(("http://", "https://", "git@"))


def _default_template() -> str:
    """In-repo template in dev checkouts, GitHub repo for installed runs."""
    root = local_template_root()
    return str(root) if root else DEFAULT_TEMPLATE
