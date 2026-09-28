"""Data models and errors for managed shell setup."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


class ShellIntegrationError(ValueError):
    """Raised when shell integration cannot be resolved safely."""


@dataclass(frozen=True, slots=True)
class ShellPaths:
    """Resolved files used by one shell integration."""

    shell: str
    rc_path: Path
    generated_path: Path


@dataclass(frozen=True, slots=True)
class ShellInstallResult:
    """Result of installing or refreshing shell integration."""

    paths: ShellPaths
    changed: bool
    backup_path: Path | None
