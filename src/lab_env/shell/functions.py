"""Render managed functions for Bash and Zsh."""

# --------------------------------------------------
# import necessary modules
# --------------------------------------------------
from __future__ import annotations


# --------------------------------------------------
# render individual functions
# --------------------------------------------------
def render_findbig() -> str:
    """Render the recursive large-file search function."""

    fcn_lines = """findbig() {
    local size="${1:-100M}"
    find . -type f -size "+${size}" -exec du -h {} +
}"""
    return fcn_lines


# --------------------------------------------------
# compose generated functions
# --------------------------------------------------
def render_functions() -> str:
    """Render managed function declarations for a generated shell file."""

    lines = [
        "# --------------------------------------------------",
        "# functions managed by lab-env",
        "# --------------------------------------------------",
        render_findbig(),
    ]
    return "\n".join(lines) + "\n"
