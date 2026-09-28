"""Shared state for lab-env CLI commands."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class CliContext:
    """Values shared by lab subcommands."""

    config_path: Path
