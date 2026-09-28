"""List configured lab host aliases."""

from __future__ import annotations

import typer

from lab_env.cli.context import CliContext
from lab_env.config import ConfigError, load_config


def cmd_hosts(context: typer.Context) -> None:
    """List configured host aliases without making connections."""

    cli_context: CliContext = context.obj
    try:
        config = load_config(cli_context.config_path)
    except ConfigError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(2) from error

    if not config.hosts:
        typer.echo("no hosts configured")
        return

    for host_name, host in sorted(config.hosts.items()):
        description = f" - {host.description}" if host.description else ""
        typer.echo(f"{host_name}: {host.destination}{description}")
