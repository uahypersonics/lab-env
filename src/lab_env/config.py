"""Personal configuration loading and validation."""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
_TOP_LEVEL_FIELDS = {"schema_version", "hosts"}
_HOST_FIELDS = {"destination", "description", "ssh_command"}


class ConfigError(ValueError):
    """Raised when personal configuration cannot be loaded or validated."""


@dataclass(frozen=True, slots=True)
class HostConfig:
    """Connection metadata for one configured host."""

    destination: str
    description: str | None = None
    ssh_command: str = "ssh"


@dataclass(frozen=True, slots=True)
class LabConfig:
    """Validated personal lab-env configuration."""

    schema_version: int = SCHEMA_VERSION
    hosts: dict[str, HostConfig] = field(default_factory=dict)


def default_config_path() -> Path:
    """Return the platform-neutral user configuration path."""

    configured_path = os.environ.get("LAB_ENV_CONFIG")
    if configured_path:
        return Path(configured_path).expanduser()

    config_root = os.environ.get("XDG_CONFIG_HOME")
    if config_root:
        return Path(config_root).expanduser() / "lab-env" / "config.toml"
    return Path.home() / ".config" / "lab-env" / "config.toml"


def initialize_config(path: Path) -> Path:
    """Create a default personal configuration without replacing existing data.

    Args:
        path: Destination configuration path.

    Returns:
        The resolved path written to disk.

    Raises:
        FileExistsError: If the destination already exists.
        OSError: If the destination cannot be created.
    """

    resolved_path = path.expanduser()
    resolved_path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    config_text = (
        "# lab-env personal configuration\n"
        f"schema_version = {SCHEMA_VERSION}\n\n"
        "# Add named SSH destinations under [hosts].\n"
        "# Authentication remains in ~/.ssh/config.\n"
        "[hosts]\n"
    )

    with resolved_path.open("x", encoding="utf-8") as stream:
        stream.write(config_text)

    return resolved_path.resolve()


def load_config(path: Path) -> LabConfig:
    """Load and strictly validate personal TOML configuration.

    Args:
        path: Configuration file path.

    Returns:
        Validated configuration.

    Raises:
        ConfigError: If the file is missing, malformed, or unsupported.
    """

    resolved_path = path.expanduser()
    try:
        with resolved_path.open("rb") as stream:
            raw_config = tomllib.load(stream)
    except FileNotFoundError as error:
        raise ConfigError(
            f"configuration not found: {resolved_path}; run 'lab --config {resolved_path} init'"
        ) from error
    except tomllib.TOMLDecodeError as error:
        raise ConfigError(f"invalid TOML in {resolved_path}: {error}") from error
    except OSError as error:
        raise ConfigError(f"cannot read configuration {resolved_path}: {error}") from error

    return _parse_config(raw_config)


def _parse_config(raw_config: dict[str, Any]) -> LabConfig:
    """Validate a decoded TOML document."""

    unknown_fields = sorted(set(raw_config) - _TOP_LEVEL_FIELDS)
    if unknown_fields:
        joined_fields = ", ".join(unknown_fields)
        raise ConfigError(f"unknown top-level configuration field(s): {joined_fields}")

    schema_version = raw_config.get("schema_version")
    if schema_version != SCHEMA_VERSION:
        raise ConfigError(
            f"unsupported schema_version {schema_version!r}; expected {SCHEMA_VERSION}"
        )

    raw_hosts = raw_config.get("hosts", {})
    if not isinstance(raw_hosts, dict):
        raise ConfigError("hosts must be a TOML table")

    hosts: dict[str, HostConfig] = {}
    for host_name, raw_host in raw_hosts.items():
        if not isinstance(raw_host, dict):
            raise ConfigError(f"hosts.{host_name} must be a TOML table")

        unknown_host_fields = sorted(set(raw_host) - _HOST_FIELDS)
        if unknown_host_fields:
            joined_fields = ", ".join(unknown_host_fields)
            raise ConfigError(f"unknown field(s) for hosts.{host_name}: {joined_fields}")

        destination = raw_host.get("destination")
        if not isinstance(destination, str) or not destination.strip():
            raise ConfigError(f"hosts.{host_name}.destination must be a non-empty string")

        description = raw_host.get("description")
        if description is not None and not isinstance(description, str):
            raise ConfigError(f"hosts.{host_name}.description must be a string")

        ssh_command = raw_host.get("ssh_command", "ssh")
        if not isinstance(ssh_command, str) or not ssh_command.strip():
            raise ConfigError(f"hosts.{host_name}.ssh_command must be a non-empty string")

        hosts[host_name] = HostConfig(
            destination=destination.strip(),
            description=description,
            ssh_command=ssh_command.strip(),
        )

    return LabConfig(schema_version=SCHEMA_VERSION, hosts=hosts)
