"""Post-render cleanup — drop files that don't apply to the chosen config."""

import shutil
from pathlib import Path

root = Path.cwd()
gateway = "{{ cookiecutter.gateway }}"
db = "{{ cookiecutter.db }}"
pattern = "{{ cookiecutter.agent_pattern }}"

if gateway == "off":
    shutil.rmtree(root / "infra", ignore_errors=True)
elif gateway == "local":
    shutil.rmtree(root / "infra/konnect", ignore_errors=True)

if pattern != "rag":
    shutil.rmtree(root / "knowledge", ignore_errors=True)

# sqlite needs no volumes; keep the file tidy regardless.
print(f"myg: generated with pattern={{ cookiecutter.agent_pattern }}, db={db}, gateway={gateway}")
