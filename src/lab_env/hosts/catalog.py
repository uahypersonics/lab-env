"""Compose the effective host catalog from shared and user-defined hosts."""

from __future__ import annotations

from collections.abc import Mapping

from lab_env.hosts.defaults import DEFAULT_HOSTS
from lab_env.hosts.models import HostConfig


def available_hosts(configured_hosts: Mapping[str, HostConfig]) -> dict[str, HostConfig]:
    """Combine shared hosts with user-configured hosts and overrides."""

    hosts = dict(DEFAULT_HOSTS)
    for host_name, configured_host in configured_hosts.items():
        default_host = hosts.get(host_name)
        if default_host is not None:
            configured_host = HostConfig(
                destination=configured_host.destination,
                description=configured_host.description or default_host.description,
                ssh_command=configured_host.ssh_command,
                transfer_destination=(
                    configured_host.transfer_destination or default_host.transfer_destination
                ),
            )
        hosts[host_name] = configured_host
    return hosts
