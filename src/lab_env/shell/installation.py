"""Install, inspect, and remove managed shell startup files."""

from __future__ import annotations

import re
import shutil
from pathlib import Path

from lab_env.shell.models import ShellInstallResult, ShellIntegrationError, ShellPaths
from lab_env.shell.rendering import (
    BASH_LOGIN_BLOCK_END,
    BASH_LOGIN_BLOCK_START,
    BLOCK_END,
    BLOCK_START,
    render_bash_login_block,
    render_generated_shell,
    render_managed_block,
)

BASHRC_SOURCE_PATTERN = re.compile(
    r"^\s*(?:source|\.)\s+(?:\"?(?:\$HOME|\$\{HOME\}|~)/\.bashrc\"?)(?:\s|$)",
    re.MULTILINE,
)


def integration_status(paths: ShellPaths) -> str:
    """Return ``installed``, ``not installed``, or ``incomplete``."""

    rc_text = _read_optional(paths.rc_path)
    rc_bounds = _managed_block_bounds(rc_text)
    login_text = ""
    login_bounds = None
    login_sources_rc = False
    if paths.login_rc_path is not None:
        login_text = _read_optional(paths.login_rc_path)
        login_bounds = _managed_block_bounds(
            login_text,
            BASH_LOGIN_BLOCK_START,
            BASH_LOGIN_BLOCK_END,
        )
        login_sources_rc = _sources_bashrc(login_text)

    if rc_bounds is None and login_bounds is None and not login_sources_rc:
        return "not installed"
    login_is_ready = paths.login_rc_path is None or login_bounds is not None or login_sources_rc
    if rc_bounds is None or not login_is_ready or not paths.generated_path.exists():
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

    managed_block = render_managed_block(paths.generated_path)

    # build all startup-file changes before writing any of them
    startup_changes: dict[Path, tuple[str, str]] = {}
    rc_text = _read_optional(paths.rc_path)
    updated_rc = _replace_managed_block(rc_text, managed_block, BLOCK_START, BLOCK_END)
    if updated_rc != rc_text:
        startup_changes[paths.rc_path] = (rc_text, updated_rc)

    if paths.login_rc_path is not None:
        login_text = _read_optional(paths.login_rc_path)
        login_bounds = _managed_block_bounds(
            login_text,
            BASH_LOGIN_BLOCK_START,
            BASH_LOGIN_BLOCK_END,
        )

        if _sources_bashrc(login_text):
            updated_login = _remove_managed_block(
                login_text,
                login_bounds,
            )
        else:
            login_block = render_bash_login_block(paths.rc_path)
            updated_login = _replace_managed_block(
                login_text,
                login_block,
                BASH_LOGIN_BLOCK_START,
                BASH_LOGIN_BLOCK_END,
            )

        if updated_login != login_text:
            startup_changes[paths.login_rc_path] = (login_text, updated_login)

    generated_text = render_generated_shell(config_path)
    backup_paths: list[Path] = []
    for startup_path, (original_text, _) in startup_changes.items():
        if startup_path.exists():
            backup_paths.append(_backup_file(startup_path))

    # write the generated static file before making the startup file source it
    paths.generated_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    paths.generated_path.write_text(generated_text, encoding="utf-8")

    for startup_path, (_, updated_text) in startup_changes.items():
        startup_path.parent.mkdir(parents=True, exist_ok=True)
        startup_path.write_text(updated_text, encoding="utf-8")

    return ShellInstallResult(
        paths=paths,
        changed=bool(startup_changes),
        backup_paths=tuple(backup_paths),
    )


def uninstall_shell(paths: ShellPaths) -> tuple[Path, ...]:
    """Remove only the managed startup block and generated shell fragment."""

    startup_paths = [(paths.rc_path, BLOCK_START, BLOCK_END)]
    if paths.login_rc_path is not None:
        startup_paths.append((paths.login_rc_path, BASH_LOGIN_BLOCK_START, BASH_LOGIN_BLOCK_END))

    startup_changes: dict[Path, tuple[str, str]] = {}
    for startup_path, block_start, block_end in startup_paths:
        current_text = _read_optional(startup_path)
        block_bounds = _managed_block_bounds(current_text, block_start, block_end)
        updated_text = _remove_managed_block(current_text, block_bounds)
        if updated_text != current_text:
            startup_changes[startup_path] = (current_text, updated_text)

    backup_paths: list[Path] = []
    for startup_path in startup_changes:
        if startup_path.exists():
            backup_paths.append(_backup_file(startup_path))

    for startup_path, (_, updated_text) in startup_changes.items():
        startup_path.write_text(updated_text, encoding="utf-8")

    if paths.generated_path.exists():
        paths.generated_path.unlink()

    return tuple(backup_paths)


def _managed_block_bounds(
    content: str,
    block_start_marker: str = BLOCK_START,
    block_end_marker: str = BLOCK_END,
) -> tuple[int, int] | None:
    """Locate one complete managed block and reject ambiguous marker state."""

    start_count = content.count(block_start_marker)
    end_count = content.count(block_end_marker)
    if start_count == 0 and end_count == 0:
        return None
    if start_count != 1 or end_count != 1:
        raise ShellIntegrationError(
            "shell startup file contains incomplete or duplicate lab-env markers"
        )

    block_start = content.index(block_start_marker)
    marker_end = content.index(block_end_marker, block_start) + len(block_end_marker)
    block_end = marker_end + 1 if content[marker_end : marker_end + 1] == "\n" else marker_end
    return block_start, block_end


def _replace_managed_block(
    content: str,
    managed_block: str,
    block_start_marker: str,
    block_end_marker: str,
) -> str:
    """Replace one managed block or append it without changing other content."""

    block_bounds = _managed_block_bounds(content, block_start_marker, block_end_marker)
    if block_bounds is None:
        separator = "" if not content or content.endswith("\n") else "\n"
        return f"{content}{separator}{managed_block}"

    block_start, block_end = block_bounds
    return content[:block_start] + managed_block + content[block_end:]


def _remove_managed_block(content: str, block_bounds: tuple[int, int] | None) -> str:
    """Remove a managed block while preserving all surrounding user content."""

    if block_bounds is None:
        return content
    block_start, block_end = block_bounds
    return content[:block_start] + content[block_end:]


def _sources_bashrc(content: str) -> bool:
    """Check for a common direct source command for the user's Bash rc file."""

    return BASHRC_SOURCE_PATTERN.search(content) is not None


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
