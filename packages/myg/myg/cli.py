"""myg CLI — your guy for agent apps."""

from __future__ import annotations

import sys

# Windows consoles default to cp1252 — unicode output must not depend on locale.
for stream in (sys.stdout, sys.stderr):
    if getattr(stream, "encoding", "") and stream.encoding.lower() not in ("utf-8", "utf8"):
        stream.reconfigure(encoding="utf-8", errors="replace")  # type: ignore[union-attr]

import typer  # noqa: E402

from myg import __version__  # noqa: E402
from myg.commands import (  # noqa: E402
    configure,
    db,
    deploy,
    dev,
    doctor,
    eject,
    init,
    prompt,
    templates,
    update,
)

app = typer.Typer(
    name="myg",
    help="Your guy for agent apps — scaffold a CopilotKit + LangGraph agent in one command.",
    no_args_is_help=True,
    rich_markup_mode="rich",
    add_completion=False,
)

app.command()(init.init)
app.command()(configure.configure)
app.command()(db.db)
app.command("db-claim")(db.claim_url)
app.command()(prompt.prompt)
app.command()(dev.dev)
app.command()(deploy.deploy)
app.command()(doctor.doctor)
app.command()(update.update)
app.command()(eject.eject)
app.command()(templates.templates)


@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(False, "--version", "-V", help="Print version"),
) -> None:
    if version:
        typer.echo(f"myg {__version__}")
        raise typer.Exit()


if __name__ == "__main__":
    app()
