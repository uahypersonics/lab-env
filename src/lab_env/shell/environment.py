"""Render managed shell environment initialization."""

from __future__ import annotations

import os
import shlex
import shutil
import subprocess
from pathlib import Path

from lab_env.config import ShellConfig

CONDA_PROFILE_PATH = Path("etc/profile.d/conda.sh")
USER_CONDA_ROOTS = ("miniforge3", "miniconda3", "anaconda3", "mambaforge")
SYSTEM_CONDA_ROOTS = (
    Path("/opt/miniforge3"),
    Path("/opt/miniconda3"),
    Path("/opt/anaconda3"),
    Path("/opt/conda"),
    Path("/opt/homebrew/Caskroom/miniforge/base"),
)


def conda_init_candidates(home: Path | None = None) -> tuple[Path, ...]:
    """Return supported Conda initialization scripts in discovery order."""

    home_path = home or Path.home()
    user_candidates = tuple(home_path / root / CONDA_PROFILE_PATH for root in USER_CONDA_ROOTS)
    system_candidates = tuple(root / CONDA_PROFILE_PATH for root in SYSTEM_CONDA_ROOTS)
    return user_candidates + system_candidates


def find_conda_init(
    explicit_path: str | None = None,
    home: Path | None = None,
) -> Path | None:
    """Return the first available Conda initialization script.

    Args:
        explicit_path: Authoritative user-configured path to ``conda.sh``.
        home: Home directory used for known-location discovery.

    Returns:
        Discovered initialization script, or ``None`` when none is available.
    """

    if explicit_path is not None:
        configured_path = Path(os.path.expandvars(explicit_path)).expanduser()
        return configured_path if configured_path.is_file() else None

    candidates: list[Path] = []
    conda_executable = os.environ.get("CONDA_EXE")
    if conda_executable:
        candidates.append(Path(conda_executable).expanduser().parent.parent / CONDA_PROFILE_PATH)

    conda_prefix = os.environ.get("CONDA_PREFIX")
    if conda_prefix:
        prefix_path = Path(conda_prefix).expanduser()
        candidates.append(prefix_path / CONDA_PROFILE_PATH)
        if prefix_path.parent.name == "envs":
            candidates.append(prefix_path.parent.parent / CONDA_PROFILE_PATH)

    conda_command = shutil.which("conda")
    if conda_command is not None:
        try:
            result = subprocess.run(
                [conda_command, "info", "--base"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
        except (OSError, subprocess.TimeoutExpired):
            pass
        else:
            if result.returncode == 0 and result.stdout.strip():
                candidates.append(Path(result.stdout.strip()) / CONDA_PROFILE_PATH)

    candidates.extend(conda_init_candidates(home))
    return next((path for path in dict.fromkeys(candidates) if path.is_file()), None)


def render_environment(config: ShellConfig) -> str:
    """Render enabled shell environment integrations."""

    if not config.initialize_conda:
        return ""

    discovered_path = find_conda_init(config.conda_init_path)
    if config.conda_init_path is not None:
        conda_paths = [
            shlex.quote(str(Path(os.path.expandvars(config.conda_init_path)).expanduser()))
        ]
    else:
        conda_paths = []
        if discovered_path is not None:
            conda_paths.append(shlex.quote(str(discovered_path)))
        conda_paths.extend(f'"$HOME/{root}/{CONDA_PROFILE_PATH}"' for root in USER_CONDA_ROOTS)
        conda_paths.extend(str(root / CONDA_PROFILE_PATH) for root in SYSTEM_CONDA_ROOTS)
        conda_paths = list(dict.fromkeys(conda_paths))

    environment_lines = [
        "# --------------------------------------------------",
        "# environment: initializes optional command-line tools",
        "# --------------------------------------------------",
        "for _lab_env_conda_sh in \\",
    ]
    for index, conda_path in enumerate(conda_paths):
        continuation = " \\" if index < len(conda_paths) - 1 else ""
        environment_lines.append(f"    {conda_path}{continuation}")
    environment_lines.extend(
        [
            "do",
            '    if [ -f "$_lab_env_conda_sh" ]; then',
            '        . "$_lab_env_conda_sh"',
            "        break",
            "    fi",
            "done",
            "unset _lab_env_conda_sh",
        ]
    )
    return "\n".join(environment_lines) + "\n"
