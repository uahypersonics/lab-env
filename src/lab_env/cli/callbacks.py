"""Shared callbacks for the lab-env command-line interface."""

from __future__ import annotations

import typer

from lab_env import __version__


def version_callback(value: bool) -> None:
    """Print the installed package version and exit."""

    if value:
        typer.echo(f"lab {__version__}")
        raise typer.Exit()
