"""Typer application for the lab-env command-line interface."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from lab_env.cli.callbacks import version_callback
from lab_env.cli.cmd_doctor import cmd_doctor
from lab_env.cli.cmd_hosts import cmd_hosts
from lab_env.cli.cmd_init import cmd_init
from lab_env.cli.cmd_shell import shell_app
from lab_env.cli.context import CliContext
from lab_env.config import default_config_path

app = typer.Typer(
    name="lab",
    help="Set up and inspect consistent research computing environments.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main(
    context: typer.Context,
    config: Annotated[
        Path | None,
        typer.Option(
            "--config",
            help="Personal TOML configuration path.",
            dir_okay=False,
        ),
    ] = None,
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-V",
            callback=version_callback,
            is_eager=True,
            help="Show the installed version and exit.",
        ),
    ] = False,
) -> None:
    """Configure shared state for lab-env commands."""

    del version
    context.obj = CliContext(config_path=config or default_config_path())


app.command(name="init", rich_help_panel="Environment")(cmd_init)
app.command(name="hosts", rich_help_panel="Environment")(cmd_hosts)
app.command(name="doctor", rich_help_panel="Environment")(cmd_doctor)
app.add_typer(shell_app, name="shell", rich_help_panel="Shell")


if __name__ == "__main__":
    app()
