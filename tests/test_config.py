"""Configuration schema tests."""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from lab_env.config import ConfigError, initialize_config, load_config


def test_initialized_config_includes_copy_ready_examples(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"

    initialize_config(config_path)

    config_text = config_path.read_text(encoding="utf-8")
    config = load_config(config_path)
    assert config.shell.initialize_conda is True
    assert config.shell.default_aliases is True
    assert "# lab-env user configuration" in config_text
    assert re.search(r"# created at: \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", config_text)
    assert "# persistent user-owned file; make and keep your changes here" in config_text
    assert "# lab init will never overwrite this file" in config_text
    assert "# basic settings: config format used by lab-env" in config_text
    assert "# shell configuration: controls generated shell integration" in config_text
    assert "initialize_conda = true" in config_text
    assert '# conda_init_path = "/path/to/etc/profile.d/conda.sh"' in config_text
    assert "# user-defined aliases: persistent commands and default overrides" in config_text
    assert "# remote hosts: named systems used by connect, pull, and push" in config_text
    assert '# gs = "git status"' in config_text
    assert "# work = 'cd \"$HOME/work\"'" in config_text
    assert '# Skip selected defaults, for example: ["rm", "cp"].' in config_text
    assert "# [hosts.cluster]" in config_text


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
