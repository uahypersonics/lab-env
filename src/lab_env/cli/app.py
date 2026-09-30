"""Typer application for the lab-env command-line interface."""

# --------------------------------------------------
# import necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from lab_env.cli.callbacks import version_callback
from lab_env.cli.cmd_doctor import cmd_doctor
from lab_env.cli.cmd_hosts import cmd_hosts
from lab_env.cli.cmd_init import cmd_init
from lab_env.cli.cmd_remote import cmd_connect, cmd_pull, cmd_push
from lab_env.cli.cmd_shell import shell_app
from lab_env.cli.cmd_tecplot import tecplot_app
from lab_env.cli.context import CliContext
from lab_env.config import default_config_path

# --------------------------------------------------
# create Typer application
# --------------------------------------------------
app = typer.Typer(
    name="lab",
    help="Set up and inspect consistent research computing environments.",
    no_args_is_help=True,
    add_completion=False,
)


# --------------------------------------------------
# callbacks: defined in callbacks.py
#   - version_callback: handles the --version option
# --------------------------------------------------
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


# --------------------------------------------------
# register commands: provided in cmd_*.py modules
# --------------------------------------------------

# init command
app.command(name="init", rich_help_panel="Configuration")(cmd_init)

# hosts command
app.command(name="hosts", rich_help_panel="Configuration")(cmd_hosts)

# doctor command
app.command(name="doctor", rich_help_panel="Diagnostics")(cmd_doctor)

# remote commands
app.command(name="connect", rich_help_panel="Remote")(cmd_connect)
app.command(name="pull", rich_help_panel="Remote")(cmd_pull)
app.command(name="push", rich_help_panel="Remote")(cmd_push)

# shell command
app.add_typer(shell_app, name="shell", rich_help_panel="Shell")

# Tecplot command
app.add_typer(tecplot_app, name="tecplot", rich_help_panel="Applications")

# --------------------------------------------------
# main entry point
# --------------------------------------------------
if __name__ == "__main__":
    app()
