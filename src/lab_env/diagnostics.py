"""Local environment diagnostics with no network side effects."""

from __future__ import annotations

import os
import shutil
from dataclasses import dataclass
from pathlib import Path

from lab_env.config import ConfigError, load_config

SUPPORTED_SHELLS = {"bash", "zsh"}
CONNECTION_CLIENTS = ("ssh", "scp", "sftp")


@dataclass(frozen=True, slots=True)
class DiagnosticResult:
    """One diagnostic check and its user-facing result."""

    name: str
    status: str
    detail: str


def run_diagnostics(config_path: Path) -> list[DiagnosticResult]:
    """Inspect local configuration, shell, and connection clients.

    Args:
        config_path: Personal configuration path to validate.

    Returns:
        Ordered diagnostic results. This function never connects to a host.
    """

    results: list[DiagnosticResult] = []

    try:
        config = load_config(config_path)
        results.append(
            DiagnosticResult(
                "config",
                "ok",
                f"{config_path.expanduser()} ({len(config.hosts)} host(s))",
            )
        )
    except ConfigError as error:
        results.append(DiagnosticResult("config", "error", str(error)))

    shell_name = Path(os.environ.get("SHELL", "")).name
    if shell_name in SUPPORTED_SHELLS:
        results.append(DiagnosticResult("shell", "ok", shell_name))
    else:
        detail = shell_name or "SHELL is not set"
        results.append(DiagnosticResult("shell", "warning", detail))

    for client_name in CONNECTION_CLIENTS:
        client_path = shutil.which(client_name)
        if client_path is None:
            results.append(DiagnosticResult(client_name, "warning", "not found on PATH"))
        else:
            results.append(DiagnosticResult(client_name, "ok", client_path))

    return results
