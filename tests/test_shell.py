"""Shell integration tests using temporary startup files."""

from __future__ import annotations

from pathlib import Path

import pytest

from lab_env.shell import (
    BLOCK_END,
    BLOCK_START,
    ShellIntegrationError,
    install_shell,
    integration_status,
    render_managed_block,
    resolve_shell_paths,
    uninstall_shell,
)


def test_install_is_idempotent_and_preserves_existing_content(tmp_path: Path) -> None:
    config_path = tmp_path / "config" / "config.toml"
    config_path.parent.mkdir()
    config_path.write_text("schema_version = 1\n[hosts]\n", encoding="utf-8")
    rc_path = tmp_path / "home" / ".zshrc"
    rc_path.parent.mkdir()
    rc_path.write_text("export EXISTING=value\n", encoding="utf-8")
    paths = resolve_shell_paths(config_path, shell="zsh", rc_path=rc_path)

    first_result = install_shell(paths, config_path)
    installed_text = rc_path.read_text(encoding="utf-8")
    second_result = install_shell(paths, config_path)

    assert first_result.changed is True
    assert first_result.backup_path is not None
    assert first_result.backup_path.read_text(encoding="utf-8") == "export EXISTING=value\n"
    assert installed_text.startswith("export EXISTING=value\n")
    assert installed_text.count(BLOCK_START) == 1
    assert installed_text.count(BLOCK_END) == 1
    assert paths.generated_path.exists()
    assert integration_status(paths) == "installed"
    assert second_result.changed is False
    assert second_result.backup_path is None


def test_uninstall_removes_only_owned_content(tmp_path: Path) -> None:
    config_path = tmp_path / "config" / "config.toml"
    rc_path = tmp_path / ".bashrc"
    rc_path.write_text("alias existing='echo existing'\n", encoding="utf-8")
    paths = resolve_shell_paths(config_path, shell="bash", rc_path=rc_path)
    install_shell(paths, config_path)

    backup_path = uninstall_shell(paths)

    assert backup_path is not None
    assert rc_path.read_text(encoding="utf-8") == "alias existing='echo existing'\n"
    assert not paths.generated_path.exists()
    assert integration_status(paths) == "not installed"


def test_preview_rendering_does_not_write_files(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    rc_path = tmp_path / ".zshrc"
    paths = resolve_shell_paths(config_path, shell="zsh", rc_path=rc_path)

    preview = render_managed_block(paths.generated_path)

    assert BLOCK_START in preview
    assert str(paths.generated_path) in preview
    assert not rc_path.exists()
    assert not paths.generated_path.exists()


def test_install_rejects_incomplete_managed_markers(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    rc_path = tmp_path / ".zshrc"
    rc_path.write_text(f"existing\n{BLOCK_START}\n", encoding="utf-8")
    paths = resolve_shell_paths(config_path, shell="zsh", rc_path=rc_path)

    with pytest.raises(ShellIntegrationError, match="incomplete or duplicate"):
        install_shell(paths, config_path)

    assert rc_path.read_text(encoding="utf-8") == f"existing\n{BLOCK_START}\n"
