"""Configuration path resolution and initialization."""

from __future__ import annotations

import os
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
    config_text = (
        "# lab-env personal configuration\n"
        f"schema_version = {SCHEMA_VERSION}\n\n"
        "# Generate the standard lab-env aliases.\n"
        "[shell]\n"
        "default_aliases = true\n\n"
        "# Disable individual defaults by name.\n"
        "disabled_aliases = []\n\n"
        "# Add or override aliases here. Quoted keys support names such as '..'.\n"
        "[shell.aliases]\n"
        '# gs = "git status"\n\n'
        "# Add named SSH destinations under [hosts].\n"
        "# Authentication remains in ~/.ssh/config.\n"
        "[hosts]\n"
    )

    with resolved_path.open("x", encoding="utf-8") as stream:
        stream.write(config_text)

    return resolved_path.resolve()
