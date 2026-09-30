"""Export Tecplot layouts through the Tecplot batch interface."""

# --------------------------------------------------
# import necessary modules
# --------------------------------------------------
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
from collections.abc import Sequence
from pathlib import Path

DEFAULT_FORMAT = "png"
DEFAULT_WIDTH = 2000
SUPPORTED_LAYOUT_SUFFIXES = {".lay", ".lpk"}


# --------------------------------------------------
# locate Tecplot
# --------------------------------------------------
def find_tecplot_executable(explicit_path: Path | None = None) -> Path:
    """Locate the Tecplot executable.

    Args:
        explicit_path: Optional executable supplied by the user.

    Returns:
        Resolved Tecplot executable path.

    Raises:
        FileNotFoundError: If no Tecplot executable can be found.
    """

    # check explicit and environment overrides first
    candidates: list[Path] = []
    if explicit_path is not None:
        candidates.append(explicit_path.expanduser())

    environment_path = os.environ.get("TECPLOT_EXE")
    if environment_path:
        candidates.append(Path(environment_path).expanduser())

    for candidate in candidates:
        if candidate.is_file():
            return candidate.resolve()

    # check the active command search path
    command_path = shutil.which("tec360")
    if command_path is not None:
        return Path(command_path).resolve()

    # check standard macOS application locations
    applications = Path("/Applications")
    app_pattern = "Tecplot 360 EX*/Tecplot 360 EX*.app/Contents/MacOS/Tecplot 360 EX*"
    app_candidates = sorted(applications.glob(app_pattern), reverse=True)
    for candidate in app_candidates:
        if candidate.is_file():
            return candidate.resolve()

    raise FileNotFoundError(
        "Tecplot executable not found; use --tecplot, set TECPLOT_EXE, or add tec360 to PATH"
    )


# --------------------------------------------------
# export layouts
# --------------------------------------------------
def export_layouts(
    layouts: Sequence[Path],
    *,
    output_format: str = DEFAULT_FORMAT,
    width: int = DEFAULT_WIDTH,
    output_dir: Path | None = None,
    tecplot_executable: Path | None = None,
) -> list[Path]:
    """Export Tecplot layout files to images.

    Args:
        layouts: Tecplot ``.lay`` or ``.lpk`` files.
        output_format: Tecplot export format, such as ``png`` or ``eps``.
        width: Output image width in pixels.
        output_dir: Optional common output directory.
        tecplot_executable: Optional Tecplot executable override.

    Returns:
        Paths to the exported images.

    Raises:
        FileNotFoundError: If an input or Tecplot executable does not exist.
        ValueError: If inputs or export settings are invalid.
        subprocess.CalledProcessError: If Tecplot exits unsuccessfully.
    """

    # validate export settings
    if not layouts:
        raise ValueError("at least one Tecplot layout is required")
    if width <= 0:
        raise ValueError("width must be greater than zero")

    normalized_format = output_format.strip().lower().lstrip(".")
    if not normalized_format or not normalized_format.isalnum():
        raise ValueError("format must contain only letters and numbers")

    # validate all layouts before starting Tecplot
    layout_paths = [Path(layout).expanduser().resolve() for layout in layouts]
    for layout_path in layout_paths:
        if not layout_path.is_file():
            raise FileNotFoundError(f"layout file not found: {layout_path}")
        if layout_path.suffix.lower() not in SUPPORTED_LAYOUT_SUFFIXES:
            raise ValueError(f"layout must use .lay or .lpk: {layout_path}")

    selected_executable = find_tecplot_executable(tecplot_executable)
    selected_output_dir = output_dir.expanduser().resolve() if output_dir is not None else None
    if selected_output_dir is not None:
        selected_output_dir.mkdir(parents=True, exist_ok=True)

    # export each layout through an isolated temporary macro
    written: list[Path] = []
    for layout_path in layout_paths:
        target_dir = selected_output_dir or layout_path.parent
        output_path = target_dir / f"{layout_path.stem}.{normalized_format}"
        macro_text = _build_export_macro(
            working_dir=layout_path.parent,
            output_path=output_path,
            output_format=normalized_format,
            width=width,
        )

        with tempfile.TemporaryDirectory(prefix="lab-env-tecplot-") as temp_dir:
            macro_path = Path(temp_dir) / "export.mcr"
            macro_path.write_text(macro_text, encoding="utf-8")
            subprocess.run(
                [
                    str(selected_executable),
                    "-b",
                    "-quiet",
                    str(layout_path),
                    str(macro_path),
                ],
                cwd=layout_path.parent,
                check=True,
            )

        if not output_path.is_file():
            raise RuntimeError(f"Tecplot completed without creating output: {output_path}")
        written.append(output_path)

    return written


# --------------------------------------------------
# build Tecplot macro
# --------------------------------------------------
def _build_export_macro(
    *,
    working_dir: Path,
    output_path: Path,
    output_format: str,
    width: int,
) -> str:
    """Build one Tecplot image-export macro."""

    # escape apostrophes used by Tecplot string literals
    macro_working_dir = str(working_dir).replace("'", "\\'")
    macro_output_path = str(output_path).replace("'", "\\'")

    lines = [
        "#!MC 1410",
        f"$!VarSet |MFBD| ='{macro_working_dir}'",
        f"$!EXPORTSETUP EXPORTFORMAT = {output_format.upper()}",
        "$!PRINTSETUP PALETTE = COLOR",
        f"$!EXPORTSETUP IMAGEWIDTH = {width}",
        f"$!EXPORTSETUP EXPORTFNAME ='{macro_output_path}'",
        "$!EXPORT",
        "  EXPORTREGION = ALLFRAMES",
        "$!RemoveVar |MFBD|",
    ]
    macro_text = "\n".join(lines) + "\n"
    return macro_text
