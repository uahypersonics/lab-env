"""Build and execute remote access commands without shell interpolation."""

from __future__ import annotations

import shlex
import subprocess
from collections.abc import Sequence
from dataclasses import dataclass
from os.path import expanduser
from typing import Literal

from lab_env.config import LabConfig
from lab_env.hosts.catalog import available_hosts
from lab_env.hosts.models import HostConfig


class RemoteCommandError(ValueError):
    """Raised when a remote command cannot be constructed or started."""


@dataclass(frozen=True, slots=True)
class CommandResult:
    """Result of preparing or running an external command."""

    arguments: tuple[str, ...]
    return_code: int | None


def resolve_host(config: LabConfig, host_name: str) -> HostConfig:
    """Resolve a configured host by name.

    Args:
        config: Validated personal configuration.
        host_name: Built-in or user-configured host name.

    Returns:
        Matching host configuration.

    Raises:
        RemoteCommandError: If the host is not configured.
    """

    hosts = available_hosts(config.hosts)
    host = hosts.get(host_name)
    if host is None:
        available = ", ".join(sorted(hosts)) or "none"
        raise RemoteCommandError(f"unknown host '{host_name}'; available hosts: {available}")
    return host


def build_connect_command(host: HostConfig, remote_args: Sequence[str] = ()) -> list[str]:
    """Build an SSH command for a configured host."""

    return [host.ssh_command, host.destination, *remote_args]


def build_transfer_command(
    direction: Literal["pull", "push"],
    host: HostConfig,
    source: str,
    destination: str,
) -> list[str]:
    """Build a resumable rsync command.

    Args:
        direction: Transfer direction relative to the local machine.
        host: Configured remote host.
        source: Source path supplied by the user.
        destination: Destination path supplied by the user.

    Returns:
        Argument list suitable for ``subprocess.run``.
    """

    remote_prefix = f"{host.destination}:"
    if direction == "pull":
        transfer_source = f"{remote_prefix}{source}"
        transfer_destination = expanduser(destination)
    else:
        transfer_source = expanduser(source)
        transfer_destination = f"{remote_prefix}{destination}"

    return [
        "rsync",
        "--archive",
        "--compress",
        "--partial",
        "--append-verify",
        "--info=progress2",
        "--rsh",
        host.ssh_command,
        transfer_source,
        transfer_destination,
    ]


def run_command(arguments: Sequence[str], *, dry_run: bool = False) -> CommandResult:
    """Run an external command directly or return its dry-run representation.

    Args:
        arguments: Executable and arguments without shell quoting.
        dry_run: Prepare the command without starting a process.

    Returns:
        Prepared arguments and process return code, if executed.

    Raises:
        RemoteCommandError: If the executable cannot be found or started.
    """

    prepared_arguments = tuple(arguments)
    if dry_run:
        return CommandResult(arguments=prepared_arguments, return_code=None)

    try:
        completed = subprocess.run(prepared_arguments, check=False)
    except FileNotFoundError as error:
        raise RemoteCommandError(f"command not found: {prepared_arguments[0]}") from error
    except OSError as error:
        raise RemoteCommandError(f"cannot start {prepared_arguments[0]}: {error}") from error

    return CommandResult(
        arguments=prepared_arguments,
        return_code=completed.returncode,
    )


def format_command(arguments: Sequence[str]) -> str:
    """Format an argument list for safe human-readable preview output."""

    return shlex.join(arguments)
