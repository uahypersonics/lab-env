"""Configuration path resolution and initialization."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from lab_env.config.classes import SCHEMA_VERSION


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
    created_at = datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")
    config_text = (
        "# --------------------------------------------------\n"
        "# lab-env user configuration\n"
        f"# created at: {created_at}\n"
        "# persistent user-owned file; make and keep your changes here\n"
        "# lab init will never overwrite this file\n"
        "# --------------------------------------------------\n\n"
        "# --------------------------------------------------\n"
        "# basic settings: config format used by lab-env\n"
        "# --------------------------------------------------\n"
        "# Do not change this value manually.\n"
        f"schema_version = {SCHEMA_VERSION}\n\n"
        "# --------------------------------------------------\n"
        "# shell configuration: controls generated shell integration\n"
        "# --------------------------------------------------\n"
        "[shell]\n"
        "# Make conda activate available for common Miniforge/Miniconda installations.\n"
        "initialize_conda = true\n"
        "# Optional explicit path for custom or module-provided Conda installations.\n"
        '# conda_init_path = "/path/to/etc/profile.d/conda.sh"\n'
        "# Generate the standard aliases defined by lab-env.\n"
        "default_aliases = true\n"
        '# Skip selected defaults, for example: ["rm", "cp"].\n'
        "disabled_aliases = []\n\n"
        "# --------------------------------------------------\n"
        "# user-defined aliases: persistent commands and default overrides\n"
        "# --------------------------------------------------\n"
        "[shell.aliases]\n"
        '# gs = "git status"\n'
        "# work = 'cd \"$HOME/work\"'\n"
        '# ll = "eza --long --header"\n\n'
        "# --------------------------------------------------\n"
        "# remote hosts: shared defaults and personal systems for connect, pull, and push\n"
        "# --------------------------------------------------\n"
        "# Built-in hosts such as uahpc are ready to use; entries here add or override hosts.\n"
        "# SSH usernames, keys, and options remain in ~/.ssh/config.\n"
        "[hosts]\n\n"
        "# Example named host and its available fields:\n"
        "# [hosts.cluster]\n"
        '# destination = "user@cluster.example.edu"\n'
        '# description = "Research cluster"\n'
        '# ssh_command = "ssh"\n'
    )

    with resolved_path.open("x", encoding="utf-8") as stream:
        stream.write(config_text)

    return resolved_path.resolve()
