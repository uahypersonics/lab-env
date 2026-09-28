"""Initialize a personal lab-env configuration."""

# --------------------------------------------------
# load necessary modules
# --------------------------------------------------
from __future__ import annotations

import typer

from lab_env.cli.context import CliContext
from lab_env.config import initialize_config


# --------------------------------------------------
# init command
# --------------------------------------------------
def cmd_init(context: typer.Context) -> None:
    """Create a personal configuration file without changing shell dotfiles."""

    cli_context: CliContext = context.obj
    try:
        config_path = initialize_config(cli_context.config_path)
    except FileExistsError:
        typer.echo(
            f"configuration already exists: {cli_context.config_path.expanduser()}",
            err=True,
        )
        raise typer.Exit(1) from None
    except OSError as error:
        typer.echo(f"error: cannot create configuration: {error}", err=True)
        raise typer.Exit(1) from error

    typer.echo(f"created configuration: {config_path}")
    typer.echo("no shell startup files were modified")
