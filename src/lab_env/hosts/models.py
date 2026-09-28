"""Data models for remote host definitions."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class HostConfig:
    """Connection metadata for one host destination."""

    destination: str
    description: str | None = None
    ssh_command: str = "ssh"
