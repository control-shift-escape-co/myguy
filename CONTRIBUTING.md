# Contributing to myg

myg exists so nobody has to hand-wire CopilotKit + LangGraph + persistence + a
gateway ever again. If that mission speaks to you, you're in the right place.

## Ground rules

- **Small PRs.** One pattern, one fix, one docs page at a time.
- **Match the style.** Python: ruff + black + basedpyright. TS: biome. Concise
  inline docs — explain *why*, skip the obvious.
- **Test the render.** If you touch `template/`, run the render smoke check:
  `python scripts/render_test.py` (renders every pattern × db × gateway combo).
- **Run the tests.** `uv run --package myg pytest packages/myg/tests` covers the
  CLI surface — add a test when you add a command or flag.
- **Funky usernames encouraged.** Not required. But your GitHub handle will end
  up immortalized in the README hall of fame, so choose wisely.

## Setup

```bash
git clone https://github.com/control-shift-escape-co/myguy
cd myguy
uv sync                    # workspace: packages/myg
pre-commit install         # ruff/black/biome hooks
uv run --package myg myg --help
```

## Layout

- `packages/myg` — the Python CLI (typer + questionary)
- `packages/create-myg` — the `npm create myg` wrapper
- `template/` — the cookiecutter template (the actual product users get)
- `docs/` — MkDocs site

## PR flow

1. Issue first for anything non-trivial — saves you wasted work.
2. Branch → commit (conventional-ish messages: `cli:`, `template:`, `docs:`).
3. CI green (lint + render smoke) → review → merge.
4. Get added to the funky-username contributor wall in the README.
