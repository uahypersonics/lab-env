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
    login_rc_path: Path | None = None

    @property
    def startup_paths(self) -> tuple[Path, ...]:
        """Return all user startup files managed for this shell."""

        if self.login_rc_path is None or self.login_rc_path == self.rc_path:
            return (self.rc_path,)
        return (self.rc_path, self.login_rc_path)


@dataclass(frozen=True, slots=True)
class ShellInstallResult:
    """Result of installing or refreshing shell integration."""

    paths: ShellPaths
    changed: bool
    backup_paths: tuple[Path, ...]

    @property
    def backup_path(self) -> Path | None:
        """Return the first backup path for single-file callers."""

        return self.backup_paths[0] if self.backup_paths else None
