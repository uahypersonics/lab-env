"""Render configured aliases for Bash and Zsh."""

from __future__ import annotations

import shlex

from lab_env.config import ShellConfig

DEFAULT_ALIASES = {
    "..": "cd ..",
    "b": "cd ..",
    "l": "ls -altr",
    "la": "ls -lah",
    "ll": "ls -lh",
    "ls": "ls -C -G -h",
    "cp": "cp -i",
    "mv": "mv -i",
    "rm": "rm -i",
}


def render_aliases(config: ShellConfig) -> str:
    """Render deterministic alias declarations for a generated shell file."""

    aliases: dict[str, str] = {}
    if config.default_aliases:
        aliases.update(DEFAULT_ALIASES)
    for alias_name in config.disabled_aliases:
        aliases.pop(alias_name, None)
    aliases.update(config.aliases)

    if not aliases:
        return ""

    lines = ["# Aliases managed by lab-env."]
    for alias_name, command in sorted(aliases.items()):
        lines.append(f"alias {alias_name}={shlex.quote(command)}")
    return "\n".join(lines) + "\n"
