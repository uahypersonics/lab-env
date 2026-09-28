"""Managed Bash and Zsh integration."""

from lab_env.shell.installation import (
    install_shell,
    integration_status,
    uninstall_shell,
)
from lab_env.shell.models import (
    ShellInstallResult,
    ShellIntegrationError,
    ShellPaths,
)
from lab_env.shell.paths import SUPPORTED_SHELLS, resolve_shell_paths
from lab_env.shell.rendering import (
    BASH_LOGIN_BLOCK_END,
    BASH_LOGIN_BLOCK_START,
    BLOCK_END,
    BLOCK_START,
    render_bash_login_block,
    render_generated_shell,
    render_managed_block,
)

__all__ = [
    "BLOCK_END",
    "BLOCK_START",
    "BASH_LOGIN_BLOCK_END",
    "BASH_LOGIN_BLOCK_START",
    "SUPPORTED_SHELLS",
    "ShellInstallResult",
    "ShellIntegrationError",
    "ShellPaths",
    "install_shell",
    "integration_status",
    "render_generated_shell",
    "render_bash_login_block",
    "render_managed_block",
    "resolve_shell_paths",
    "uninstall_shell",
]
