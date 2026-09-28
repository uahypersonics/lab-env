"""Resolve managed shell startup and generated-file paths."""

from __future__ import annotations

import os
from pathlib import Path

from lab_env.shell.models import ShellIntegrationError, ShellPaths

SUPPORTED_SHELLS = {"bash": ".bashrc", "zsh": ".zshrc"}
BASH_LOGIN_FILES = (".bash_profile", ".bash_login", ".profile")


def resolve_shell_paths(
    config_path: Path,
    shell: str | None = None,
    rc_path: Path | None = None,
) -> ShellPaths:
    """Resolve shell, startup file, and generated fragment paths.

    Args:
        config_path: Personal lab-env configuration path.
        shell: Explicit shell name. Defaults to the basename of ``$SHELL``.
        rc_path: Explicit startup file, primarily useful for controlled setups.

    Returns:
        Resolved shell integration paths.

    Raises:
        ShellIntegrationError: If the shell is unsupported or cannot be detected.
    """

    shell_name = shell or Path(os.environ.get("SHELL", "")).name
    shell_name = shell_name.strip().lower()
    if shell_name not in SUPPORTED_SHELLS:
        supported = ", ".join(sorted(SUPPORTED_SHELLS))
        detected = shell_name or "unknown"
        raise ShellIntegrationError(f"unsupported shell '{detected}'; choose one of: {supported}")

    resolved_config = config_path.expanduser().resolve()
    home_path = Path.home()
    resolved_rc = (rc_path or home_path / SUPPORTED_SHELLS[shell_name]).expanduser()
    login_rc_path = None
    if shell_name == "bash" and rc_path is None:
        login_rc_path = next(
            (home_path / name for name in BASH_LOGIN_FILES if (home_path / name).exists()),
            home_path / BASH_LOGIN_FILES[0],
        )
    generated_path = resolved_config.parent / "shell" / f"{shell_name}.sh"
    return ShellPaths(
        shell=shell_name,
        rc_path=resolved_rc,
        generated_path=generated_path,
        login_rc_path=login_rc_path,
    )
