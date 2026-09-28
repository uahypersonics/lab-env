"""Configuration schema tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from lab_env.config import ConfigError, load_config


def test_host_uses_configured_ssh_command(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "schema_version = 1\n\n"
        "[hosts.cluster]\n"
        'destination = "cluster-alias"\n'
        'ssh_command = "/opt/ossh/bin/ssh"\n',
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.hosts["cluster"].ssh_command == "/opt/ossh/bin/ssh"


def test_host_defaults_to_standard_ssh(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        'schema_version = 1\n\n[hosts.cluster]\ndestination = "cluster-alias"\n',
        encoding="utf-8",
    )

    config = load_config(config_path)

    assert config.hosts["cluster"].ssh_command == "ssh"


def test_invalid_shell_alias_name_is_rejected(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        'schema_version = 1\n\n[shell.aliases]\n"bad name" = "echo nope"\n',
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="shell alias name is invalid"):
        load_config(config_path)


def test_multiline_shell_alias_is_rejected(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        'schema_version = 1\n\n[shell.aliases]\nbad = """echo first\necho second"""\n',
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="single-line command"):
        load_config(config_path)


def test_removed_safety_aliases_field_is_rejected(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "schema_version = 1\n\n[shell]\nsafety_aliases = true\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="unknown field.*safety_aliases"):
        load_config(config_path)


def test_unknown_top_level_field_is_rejected(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "schema_version = 1\nunknown = true\n[hosts]\n",
        encoding="utf-8",
    )

    with pytest.raises(ConfigError, match="unknown top-level"):
        load_config(config_path)


def test_unsupported_schema_version_is_rejected(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text("schema_version = 99\n[hosts]\n", encoding="utf-8")

    with pytest.raises(ConfigError, match="unsupported schema_version"):
        load_config(config_path)
