"""Install, inspect, and remove managed shell startup files."""

from __future__ import annotations

import shutil
from pathlib import Path

from lab_env.shell.models import ShellInstallResult, ShellIntegrationError, ShellPaths
from lab_env.shell.rendering import (
    BLOCK_END,
    BLOCK_START,
    render_generated_shell,
    render_managed_block,
)


def integration_status(paths: ShellPaths) -> str:
    """Return ``installed``, ``not installed``, or ``incomplete``."""

    if not paths.rc_path.exists():
        return "not installed"

    rc_text = paths.rc_path.read_text(encoding="utf-8")
    start_count = rc_text.count(BLOCK_START)
    end_count = rc_text.count(BLOCK_END)
    if start_count == 0 and end_count == 0:
        return "not installed"
    if start_count != 1 or end_count != 1 or not paths.generated_path.exists():
        return "incomplete"
    return "installed"


def install_shell(paths: ShellPaths, config_path: Path) -> ShellInstallResult:
    """Install or refresh shell integration without replacing dotfiles.

    Args:
        paths: Resolved shell integration paths.
        config_path: Valid personal configuration loaded by the shell fragment.

    Returns:
        Installation result including any backup path.

    Raises:
        ShellIntegrationError: If existing managed markers are malformed.
    """

    current_text = _read_optional(paths.rc_path)
    block_bounds = _managed_block_bounds(current_text)
    generated_text = render_generated_shell(config_path)
    managed_block = render_managed_block(paths.generated_path)

    # preserve an existing valid block and normalize only its owned contents
    if block_bounds is None:
        separator = "" if not current_text or current_text.endswith("\n") else "\n"
        updated_text = f"{current_text}{separator}{managed_block}"
    else:
        block_start, block_end = block_bounds
        updated_text = current_text[:block_start] + managed_block + current_text[block_end:]

    changed = updated_text != current_text
    backup_path = _backup_file(paths.rc_path) if changed and paths.rc_path.exists() else None

    # write the generated static file before making the startup file source it
    paths.generated_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    paths.generated_path.write_text(generated_text, encoding="utf-8")

    if changed:
        paths.rc_path.parent.mkdir(parents=True, exist_ok=True)
        paths.rc_path.write_text(updated_text, encoding="utf-8")

    return ShellInstallResult(paths=paths, changed=changed, backup_path=backup_path)


def uninstall_shell(paths: ShellPaths) -> Path | None:
    """Remove only the managed startup block and generated shell fragment."""

    current_text = _read_optional(paths.rc_path)
    block_bounds = _managed_block_bounds(current_text)
    backup_path: Path | None = None

    if block_bounds is not None:
        block_start, block_end = block_bounds
        updated_text = current_text[:block_start] + current_text[block_end:]
        backup_path = _backup_file(paths.rc_path)
        paths.rc_path.write_text(updated_text, encoding="utf-8")

    if paths.generated_path.exists():
        paths.generated_path.unlink()

    return backup_path


def _managed_block_bounds(content: str) -> tuple[int, int] | None:
    """Locate one complete managed block and reject ambiguous marker state."""

    start_count = content.count(BLOCK_START)
    end_count = content.count(BLOCK_END)
    if start_count == 0 and end_count == 0:
        return None
    if start_count != 1 or end_count != 1:
        raise ShellIntegrationError(
            "shell startup file contains incomplete or duplicate lab-env markers"
        )

    block_start = content.index(BLOCK_START)
    marker_end = content.index(BLOCK_END, block_start) + len(BLOCK_END)
    block_end = marker_end + 1 if content[marker_end : marker_end + 1] == "\n" else marker_end
    return block_start, block_end


def _read_optional(path: Path) -> str:
    """Read a text file or return an empty value when it does not exist."""

    if not path.exists():
        return ""
    if path.is_symlink():
        raise ShellIntegrationError(f"refusing to modify symlinked startup file: {path}")
    return path.read_text(encoding="utf-8")


def _backup_file(path: Path) -> Path:
    """Create a non-overwriting backup beside a file."""

    backup_index = 0
    while True:
        suffix = ".lab-env.bak" if backup_index == 0 else f".lab-env.bak.{backup_index}"
        backup_path = path.with_name(f"{path.name}{suffix}")
        if not backup_path.exists():
            shutil.copy2(path, backup_path)
            return backup_path
        backup_index += 1
