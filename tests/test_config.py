"""Configuration schema tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from lab_env.config import ConfigError, load_config


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
