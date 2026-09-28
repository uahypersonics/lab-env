"""Managed Bash and Zsh integration."""

from lab_env.shell.integration import (
    BLOCK_END,
    BLOCK_START,
    SUPPORTED_SHELLS,
    ShellInstallResult,
    ShellIntegrationError,
    ShellPaths,
    install_shell,
    integration_status,
    render_generated_shell,
    render_managed_block,
    resolve_shell_paths,
    uninstall_shell,
)

__all__ = [
    "BLOCK_END",
    "BLOCK_START",
    "SUPPORTED_SHELLS",
    "ShellInstallResult",
    "ShellIntegrationError",
    "ShellPaths",
    "install_shell",
    "integration_status",
    "render_generated_shell",
    "render_managed_block",
    "resolve_shell_paths",
    "uninstall_shell",
]
