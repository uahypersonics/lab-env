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


def render_qs() -> str:
    """Render a queue shortcut that selects Slurm or PBS at runtime."""

    fcn_lines = """qs() {
    local scheduler_user="${USER:-$(id -un)}"
    if command -v squeue >/dev/null 2>&1; then
        squeue -u "$scheduler_user" "$@"
    elif command -v qstat >/dev/null 2>&1; then
        qstat -u "$scheduler_user" "$@"
    else
        printf '%s\\n' 'qs: neither squeue (Slurm) nor qstat (PBS) was found on PATH' >&2
        return 127
    fi
}"""
    return fcn_lines


def render_lay2pic() -> str:
    """Render the legacy-compatible Tecplot export shortcut."""

    fcn_lines = """lay2pic() {
    lab tecplot export "$@"
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
        render_qs(),
        render_lay2pic(),
    ]
    return "\n".join(lines) + "\n"
