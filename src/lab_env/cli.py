"""Command-line interface for lab-env."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Annotated

import typer

from lab_env import __version__
from lab_env.config import ConfigError, default_config_path, initialize_config, load_config
from lab_env.diagnostics import run_diagnostics
from lab_env.shell import (
    ShellIntegrationError,
    ShellPaths,
    install_shell,
    integration_status,
    render_generated_shell,
    render_managed_block,
    resolve_shell_paths,
    uninstall_shell,
)

app = typer.Typer(
    name="lab",
    help="Set up and inspect consistent research computing environments.",
    no_args_is_help=True,
)
shell_app = typer.Typer(help="Preview and manage shell startup integration.")
app.add_typer(shell_app, name="shell")


@dataclass(slots=True)
class CliContext:
    """Values shared by lab subcommands."""

    config_path: Path


def _version_callback(value: bool) -> None:
    """Print the installed package version and exit."""

    if value:
        typer.echo(f"lab {__version__}")
        raise typer.Exit()


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
            callback=_version_callback,
            is_eager=True,
            help="Show the installed version and exit.",
        ),
    ] = False,
) -> None:
    """Configure the shared command context."""

    del version
    context.obj = CliContext(config_path=config or default_config_path())


@app.command("init")
def init_command(context: typer.Context) -> None:
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


@app.command("hosts")
def hosts_command(context: typer.Context) -> None:
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


@app.command("doctor")
def doctor_command(context: typer.Context) -> None:
    """Check local configuration and tools without network activity."""

    cli_context: CliContext = context.obj
    results = run_diagnostics(cli_context.config_path)
    for result in results:
        typer.echo(f"[{result.status}] {result.name}: {result.detail}")

    if any(result.status == "error" for result in results):
        raise typer.Exit(1)


def _resolve_cli_shell_paths(
    context: typer.Context,
    shell_name: str | None,
    rc_path: Path | None,
) -> ShellPaths:
    """Resolve shell paths or convert validation errors to CLI failures."""

    cli_context: CliContext = context.obj
    try:
        return resolve_shell_paths(
            cli_context.config_path,
            shell=shell_name,
            rc_path=rc_path,
        )
    except ShellIntegrationError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(2) from error


@shell_app.command("preview")
def shell_preview_command(
    context: typer.Context,
    shell_name: Annotated[
        str | None,
        typer.Option("--shell", help="Shell to configure: bash or zsh."),
    ] = None,
    rc_path: Annotated[
        Path | None,
        typer.Option("--rc", help="Override the shell startup file."),
    ] = None,
) -> None:
    """Show generated files and dotfile changes without writing anything."""

    cli_context: CliContext = context.obj
    try:
        load_config(cli_context.config_path)
    except ConfigError as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(2) from error

    paths = _resolve_cli_shell_paths(context, shell_name, rc_path)
    typer.echo(f"shell: {paths.shell}")
    typer.echo(f"startup file: {paths.rc_path}")
    typer.echo(f"generated file: {paths.generated_path}")
    typer.echo("\ngenerated shell file:\n")
    typer.echo(render_generated_shell(cli_context.config_path), nl=False)
    typer.echo("\nmanaged startup block:\n")
    typer.echo(render_managed_block(paths.generated_path), nl=False)


@shell_app.command("install")
def shell_install_command(
    context: typer.Context,
    shell_name: Annotated[
        str | None,
        typer.Option("--shell", help="Shell to configure: bash or zsh."),
    ] = None,
    rc_path: Annotated[
        Path | None,
        typer.Option("--rc", help="Override the shell startup file."),
    ] = None,
) -> None:
    """Install an idempotent managed block in the shell startup file."""

    cli_context: CliContext = context.obj
    try:
        load_config(cli_context.config_path)
        paths = resolve_shell_paths(
            cli_context.config_path,
            shell=shell_name,
            rc_path=rc_path,
        )
        result = install_shell(paths, cli_context.config_path)
    except (ConfigError, OSError, ShellIntegrationError) as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(1) from error

    if result.changed:
        typer.echo(f"installed lab-env shell integration in {paths.rc_path}")
        if result.backup_path is not None:
            typer.echo(f"backup: {result.backup_path}")
    else:
        typer.echo(f"shell integration already installed: {paths.rc_path}")
    typer.echo(f"generated: {paths.generated_path}")
    typer.echo(f"activate now: source {paths.rc_path}")


@shell_app.command("status")
def shell_status_command(
    context: typer.Context,
    shell_name: Annotated[
        str | None,
        typer.Option("--shell", help="Shell to inspect: bash or zsh."),
    ] = None,
    rc_path: Annotated[
        Path | None,
        typer.Option("--rc", help="Override the shell startup file."),
    ] = None,
) -> None:
    """Report whether shell integration is installed and complete."""

    paths = _resolve_cli_shell_paths(context, shell_name, rc_path)
    status = integration_status(paths)
    typer.echo(f"{paths.shell}: {status}")
    typer.echo(f"startup file: {paths.rc_path}")
    typer.echo(f"generated file: {paths.generated_path}")
    if status == "incomplete":
        raise typer.Exit(1)


@shell_app.command("uninstall")
def shell_uninstall_command(
    context: typer.Context,
    shell_name: Annotated[
        str | None,
        typer.Option("--shell", help="Shell to configure: bash or zsh."),
    ] = None,
    rc_path: Annotated[
        Path | None,
        typer.Option("--rc", help="Override the shell startup file."),
    ] = None,
) -> None:
    """Remove only lab-env-owned shell startup content."""

    paths = _resolve_cli_shell_paths(context, shell_name, rc_path)
    try:
        previous_status = integration_status(paths)
        backup_path = uninstall_shell(paths)
    except (OSError, ShellIntegrationError) as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(1) from error

    if previous_status == "not installed":
        typer.echo(f"shell integration is not installed: {paths.rc_path}")
        return

    typer.echo(f"removed lab-env shell integration from {paths.rc_path}")
    if backup_path is not None:
        typer.echo(f"backup: {backup_path}")
