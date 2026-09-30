"""Tecplot command group."""

# --------------------------------------------------
# import necessary modules
# --------------------------------------------------
from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer

from lab_env.tecplot import export_layouts
from lab_env.tecplot.export import DEFAULT_FORMAT, DEFAULT_WIDTH

# --------------------------------------------------
# Tecplot command group
# --------------------------------------------------
tecplot_app = typer.Typer(
    help="Run portable Tecplot command wrappers.",
    no_args_is_help=True,
)


# --------------------------------------------------
# export command
# --------------------------------------------------
@tecplot_app.command("export")
def cmd_tecplot_export(
    layouts: Annotated[
        list[Path],
        typer.Argument(help="Tecplot .lay or .lpk files to export."),
    ],
    output_format: Annotated[
        str,
        typer.Option("--format", "-f", help="Tecplot image format."),
    ] = DEFAULT_FORMAT,
    width: Annotated[
        int,
        typer.Option("--width", "-w", min=1, help="Image width in pixels."),
    ] = DEFAULT_WIDTH,
    output_dir: Annotated[
        Path | None,
        typer.Option("--output-dir", "-o", help="Common output directory."),
    ] = None,
    tecplot_executable: Annotated[
        Path | None,
        typer.Option("--tecplot", help="Tecplot executable path."),
    ] = None,
) -> None:
    """Export Tecplot layouts to image files."""

    try:
        files = export_layouts(
            layouts,
            output_format=output_format,
            width=width,
            output_dir=output_dir,
            tecplot_executable=tecplot_executable,
        )
    except (FileNotFoundError, RuntimeError, ValueError) as exc:
        typer.echo(f"error: {exc}", err=True)
        raise typer.Exit(1) from exc

    typer.echo(f"wrote {len(files)} file(s)")
    for file_path in files:
        typer.echo(file_path)
