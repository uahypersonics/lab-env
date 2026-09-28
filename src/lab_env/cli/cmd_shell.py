"""Preview and manage lab-env shell startup integration."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from lab_env.cli.context import CliContext
from lab_env.config import ConfigError, load_config
from lab_env.shell import (
    ShellIntegrationError,
    ShellPaths,
    install_shell,
    integration_status,
    render_bash_login_block,
    render_generated_shell,
    render_managed_block,
    resolve_shell_paths,
    uninstall_shell,
)

shell_app = typer.Typer(
    help="Preview and manage shell startup integration.",
    no_args_is_help=True,
    add_completion=False,
)


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
    if paths.login_rc_path is not None:
        typer.echo(f"login startup file: {paths.login_rc_path}")
    typer.echo(f"generated file: {paths.generated_path}")
    typer.echo("\ngenerated shell file:\n")
    typer.echo(render_generated_shell(cli_context.config_path), nl=False)
    typer.echo("\nmanaged startup block:\n")
    typer.echo(render_managed_block(paths.generated_path), nl=False)
    if paths.login_rc_path is not None:
        typer.echo("\nBash login bridge (used unless the profile already sources .bashrc):\n")
        typer.echo(render_bash_login_block(paths.rc_path), nl=False)


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
    """Install managed shell startup integration for login and interactive shells."""

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

    startup_files = ", ".join(str(path) for path in paths.startup_paths)
    if result.changed:
        typer.echo(f"installed lab-env shell integration in {startup_files}")
        for backup_path in result.backup_paths:
            typer.echo(f"backup: {backup_path}")
    else:
        typer.echo(f"shell integration already installed: {startup_files}")
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
    if paths.login_rc_path is not None:
        typer.echo(f"login startup file: {paths.login_rc_path}")
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
        backup_paths = uninstall_shell(paths)
    except (OSError, ShellIntegrationError) as error:
        typer.echo(f"error: {error}", err=True)
        raise typer.Exit(1) from error

    if previous_status == "not installed":
        typer.echo(f"shell integration is not installed: {paths.rc_path}")
        return

    typer.echo(f"removed lab-env shell integration from {', '.join(map(str, paths.startup_paths))}")
    for backup_path in backup_paths:
        typer.echo(f"backup: {backup_path}")
