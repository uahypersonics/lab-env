"""Run local lab-env diagnostics."""

from __future__ import annotations

import typer

from lab_env.cli.context import CliContext
from lab_env.diagnostics import run_diagnostics


def cmd_doctor(context: typer.Context) -> None:
    """Check local configuration and tools without network activity."""

    cli_context: CliContext = context.obj
    results = run_diagnostics(cli_context.config_path)
    for result in results:
        typer.echo(f"[{result.status}] {result.name}: {result.detail}")

    if any(result.status == "error" for result in results):
        raise typer.Exit(1)
