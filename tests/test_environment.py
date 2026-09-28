"""Shell environment discovery tests."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path
from unittest.mock import patch

from lab_env.shell.environment import CONDA_PROFILE_PATH, find_conda_init


def _create_conda_profile(root: Path) -> Path:
    """Create and return a minimal Conda initialization script."""

    profile_path = root / CONDA_PROFILE_PATH
    profile_path.parent.mkdir(parents=True)
    profile_path.write_text("# test conda initialization\n", encoding="utf-8")
    return profile_path


def test_explicit_conda_path_is_authoritative(tmp_path: Path) -> None:
    explicit_profile = _create_conda_profile(tmp_path / "custom-conda")

    assert find_conda_init(str(explicit_profile)) == explicit_profile
    assert find_conda_init(str(tmp_path / "missing-conda.sh")) is None


def test_conda_exe_environment_variable_finds_installation(tmp_path: Path) -> None:
    conda_root = tmp_path / "miniconda3"
    profile_path = _create_conda_profile(conda_root)

    with patch.dict(os.environ, {"CONDA_EXE": str(conda_root / "bin" / "conda")}, clear=True):
        assert find_conda_init(home=tmp_path / "empty-home") == profile_path


def test_conda_info_finds_installation_base(tmp_path: Path) -> None:
    conda_root = tmp_path / "module-conda"
    profile_path = _create_conda_profile(conda_root)
    completed = subprocess.CompletedProcess(
        args=["/module/bin/conda", "info", "--base"],
        returncode=0,
        stdout=f"{conda_root}\n",
        stderr="",
    )

    with (
        patch.dict(os.environ, {}, clear=True),
        patch("lab_env.shell.environment.shutil.which", return_value="/module/bin/conda"),
        patch("lab_env.shell.environment.subprocess.run", return_value=completed),
    ):
        assert find_conda_init(home=tmp_path / "empty-home") == profile_path
