"""Render configured aliases for Bash and Zsh."""

# --------------------------------------------------
# import necessary modules
# --------------------------------------------------
from __future__ import annotations

import shlex
import sys

from lab_env.config import ShellConfig

# --------------------------------------------------
# define default aliases
# --------------------------------------------------
DEFAULT_ALIASES = {
    "..": "cd ..",
    "b": "cd ..",
    "l": "ls -altr",
    "la": "ls -lah",
    "ll": "ls -lh",
    "cp": "cp -i",
    "mv": "mv -i",
    "rm": "rm -i",
    "edit": "emacs -nw",
}


# --------------------------------------------------
# function to write aliases to file
# --------------------------------------------------
def render_aliases(config: ShellConfig) -> str:
    """Render deterministic alias declarations for a generated shell file."""

    aliases: dict[str, str] = {}
    if config.default_aliases:
        aliases.update(DEFAULT_ALIASES)
        aliases["ls"] = _default_ls_alias()
    for alias_name in config.disabled_aliases:
        aliases.pop(alias_name, None)
    aliases.update(config.aliases)

    if not aliases:
        return ""

    # info lines to which aliases will follow
    lines = [
        "# --------------------------------------------------",
        "# aliases managed by lab-env",
        "# --------------------------------------------------",
    ]
    for alias_name, command in sorted(aliases.items()):
        lines.append(f"alias {alias_name}={shlex.quote(command)}")
    return "\n".join(lines) + "\n"


def _default_ls_alias() -> str:
    """Return the colorized listing alias for the current operating system."""

    if sys.platform == "darwin":
        return "ls -C -G -h"
    return "ls --color=auto -C -h"
