"""TOML configuration loading and strict schema validation."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path
from typing import Any

from lab_env.config.classes import (
    SCHEMA_VERSION,
    ConfigError,
    LabConfig,
    ShellConfig,
)
from lab_env.hosts.models import HostConfig

_TOP_LEVEL_FIELDS = {"schema_version", "hosts", "shell"}
_HOST_FIELDS = {"destination", "description", "ssh_command", "transfer_destination"}
_SHELL_FIELDS = {
    "aliases",
    "conda_init_path",
    "default_aliases",
    "disabled_aliases",
    "initialize_conda",
}
_ALIAS_NAME_PATTERN = re.compile(r"^[A-Za-z0-9_.-]+$")


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

        transfer_destination = raw_host.get("transfer_destination")
        if transfer_destination is not None and (
            not isinstance(transfer_destination, str) or not transfer_destination.strip()
        ):
            raise ConfigError(f"hosts.{host_name}.transfer_destination must be a non-empty string")

        hosts[host_name] = HostConfig(
            destination=destination.strip(),
            description=description,
            ssh_command=ssh_command.strip(),
            transfer_destination=(
                transfer_destination.strip() if transfer_destination is not None else None
            ),
        )

    shell = _parse_shell(raw_config.get("shell", {}))
    return LabConfig(schema_version=SCHEMA_VERSION, hosts=hosts, shell=shell)


def _parse_shell(raw_shell: Any) -> ShellConfig:
    """Validate shell alias configuration."""

    if not isinstance(raw_shell, dict):
        raise ConfigError("shell must be a TOML table")

    unknown_shell_fields = sorted(set(raw_shell) - _SHELL_FIELDS)
    if unknown_shell_fields:
        joined_fields = ", ".join(unknown_shell_fields)
        raise ConfigError(f"unknown field(s) for shell: {joined_fields}")

    initialize_conda = raw_shell.get("initialize_conda", True)
    if not isinstance(initialize_conda, bool):
        raise ConfigError("shell.initialize_conda must be a boolean")

    conda_init_path = raw_shell.get("conda_init_path")
    if conda_init_path is not None and (
        not isinstance(conda_init_path, str) or not conda_init_path.strip()
    ):
        raise ConfigError("shell.conda_init_path must be a non-empty string")

    default_aliases = raw_shell.get("default_aliases", True)
    if not isinstance(default_aliases, bool):
        raise ConfigError("shell.default_aliases must be a boolean")

    raw_disabled_aliases = raw_shell.get("disabled_aliases", [])
    if not isinstance(raw_disabled_aliases, list):
        raise ConfigError("shell.disabled_aliases must be an array")

    disabled_aliases: list[str] = []
    for alias_name in raw_disabled_aliases:
        if not isinstance(alias_name, str) or not _ALIAS_NAME_PATTERN.fullmatch(alias_name):
            raise ConfigError(f"disabled shell alias name is invalid: {alias_name!r}")
        disabled_aliases.append(alias_name)

    raw_aliases = raw_shell.get("aliases", {})
    if not isinstance(raw_aliases, dict):
        raise ConfigError("shell.aliases must be a TOML table")

    aliases: dict[str, str] = {}
    for alias_name, command in raw_aliases.items():
        if not _ALIAS_NAME_PATTERN.fullmatch(alias_name):
            raise ConfigError(f"shell alias name is invalid: {alias_name!r}")
        if not isinstance(command, str) or not command.strip():
            raise ConfigError(f"shell.aliases.{alias_name} must be a non-empty string")
        if "\n" in command or "\r" in command:
            raise ConfigError(f"shell.aliases.{alias_name} must be a single-line command")
        aliases[alias_name] = command.strip()

    return ShellConfig(
        initialize_conda=initialize_conda,
        conda_init_path=conda_init_path.strip() if conda_init_path is not None else None,
        default_aliases=default_aliases,
        disabled_aliases=tuple(disabled_aliases),
        aliases=aliases,
    )
