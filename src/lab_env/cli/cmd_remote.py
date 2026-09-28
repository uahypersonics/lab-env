"""Connect to configured hosts and transfer files."""

from __future__ import annotations

from typing import Annotated

import typer

from lab_env.cli.context import CliContext
from lab_env.config import ConfigError, HostConfig, load_config
from lab_env.remote import (
    RemoteCommandError,
    build_connect_command,
    build_transfer_command,
    format_command,
    resolve_host,
    run_command,
)


def _load_cli_host(context: typer.Context, host_name: str) -> HostConfig:
    """Load one host or convert configuration errors to CLI failures."""

    cli_context: CliContext = context.obj
    try:
        config = load_config(cli_context.config_path)
        return resolve_host(config, host_name)
    except (ConfigError, RemoteCommandError) as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(2) from error


def _execute(arguments: list[str], dry_run: bool) -> None:
    """Run one command and preserve its process exit status."""

    if dry_run:
        typer.echo(format_command(arguments))
        return

    try:
        result = run_command(arguments)
    except RemoteCommandError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(1) from error

    if result.return_code:
        raise typer.Exit(result.return_code)


def cmd_connect(
    context: typer.Context,
    host_name: Annotated[str, typer.Argument(help="Configured host name.")],
    remote_args: Annotated[
        list[str] | None,
        typer.Argument(help="Optional command and arguments to run remotely."),
    ] = None,
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the SSH command without running it."),
    ] = False,
) -> None:
    """Open SSH or run a command on a configured host."""

    host = _load_cli_host(context, host_name)
    arguments = build_connect_command(host, remote_args or ())
    _execute(arguments, dry_run)


def cmd_pull(
    context: typer.Context,
    host_name: Annotated[str, typer.Argument(help="Configured host name.")],
    remote_path: Annotated[str, typer.Argument(help="Remote source path.")],
    local_path: Annotated[
        str,
        typer.Argument(help="Local destination path."),
    ] = ".",
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the rsync command without running it."),
    ] = False,
) -> None:
    """Pull files from a configured host with resumable rsync."""

    host = _load_cli_host(context, host_name)
    arguments = build_transfer_command(
        "pull",
        host,
        remote_path,
        local_path,
    )
    _execute(arguments, dry_run)



def cmd_push(
    context: typer.Context,
    host_name: Annotated[str, typer.Argument(help="Configured host name.")],
    local_path: Annotated[str, typer.Argument(help="Local source path.")],
    remote_path: Annotated[str, typer.Argument(help="Remote destination path.")],
    dry_run: Annotated[
        bool,
        typer.Option("--dry-run", help="Print the rsync command without running it."),
    ] = False,
) -> None:
    """Push files to a configured host with resumable rsync."""

    host = _load_cli_host(context, host_name)
    arguments = build_transfer_command(
        "push",
        host,
        local_path,
        remote_path,
    )
    _execute(arguments, dry_run)
