"""Command-line behavior tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from lab_env.cli import app

runner = CliRunner()


def test_help_and_version() -> None:
    help_result = runner.invoke(app, ["--help"])
    version_result = runner.invoke(app, ["--version"])

    assert help_result.exit_code == 0
    assert "init" in help_result.output
    assert "hosts" in help_result.output
    assert "doctor" in help_result.output
    assert "connect" in help_result.output
    assert "pull" in help_result.output
    assert "push" in help_result.output
    assert "shell" in help_result.output
    assert "tecplot" in help_result.output
    assert "Configuration" in help_result.output
    assert "Diagnostics" in help_result.output
    assert "Remote" in help_result.output
    assert "Shell" in help_result.output
    assert version_result.exit_code == 0
    assert version_result.output.startswith("lab ")


@patch("lab_env.cli.cmd_tecplot.export_layouts")
def test_tecplot_export_uses_png_and_width_2000_by_default(
    mock_export_layouts, tmp_path: Path
) -> None:
    layout_path = tmp_path / "figure.lay"
    output_path = tmp_path / "figure.png"
    mock_export_layouts.return_value = [output_path]

    result = runner.invoke(app, ["tecplot", "export", str(layout_path)])

    assert result.exit_code == 0
    mock_export_layouts.assert_called_once_with(
        [layout_path],
        output_format="png",
        width=2000,
        output_dir=None,
        tecplot_executable=None,
    )
    assert str(output_path) in result.output


def test_init_creates_config_without_overwriting(tmp_path: Path) -> None:
    config_path = tmp_path / "personal" / "config.toml"

    first_result = runner.invoke(app, ["--config", str(config_path), "init"])
    original_text = config_path.read_text(encoding="utf-8")
    second_result = runner.invoke(app, ["--config", str(config_path), "init"])

    assert first_result.exit_code == 0
    assert "no shell startup files were modified" in first_result.output
    assert "schema_version = 1" in original_text
    assert second_result.exit_code == 1
    assert config_path.read_text(encoding="utf-8") == original_text


def test_hosts_lists_valid_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "schema_version = 1\n\n"
        "[hosts.example]\n"
        'destination = "example-alias"\n'
        'description = "Fictitious development host"\n',
        encoding="utf-8",
    )

    result = runner.invoke(app, ["--config", str(config_path), "hosts"])

    assert result.exit_code == 0
    assert (
        "uahpc: hpc.arizona.edu - University of Arizona HPC "
        "(file transfers: filexfer.hpc.arizona.edu)"
    ) in result.output
    assert "example: example-alias - Fictitious development host" in result.output


def test_builtin_host_can_be_used_without_local_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text("schema_version = 1\n[hosts]\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["--config", str(config_path), "connect", "uahpc", "--dry-run"],
    )
    pull_result = runner.invoke(
        app,
        ["--config", str(config_path), "pull", "uahpc", "/project/data/", "./data/", "--dry-run"],
    )

    assert result.exit_code == 0
    assert result.output.strip() == "ssh hpc.arizona.edu"
    assert pull_result.exit_code == 0
    assert "filexfer.hpc.arizona.edu:/project/data/" in pull_result.output


def test_hosts_reports_missing_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.toml"

    result = runner.invoke(app, ["--config", str(config_path), "hosts"])

    assert result.exit_code == 2
    assert "configuration not found" in result.output


def test_doctor_checks_local_environment_without_network(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text("schema_version = 1\n[hosts]\n", encoding="utf-8")

    with (
        patch.dict("os.environ", {"SHELL": "/bin/zsh"}),
        patch("lab_env.diagnostics.find_conda_init", return_value=Path("/fake/conda.sh")),
        patch("lab_env.diagnostics.shutil.which", side_effect=lambda name: f"/fake/{name}"),
    ):
        result = runner.invoke(app, ["--config", str(config_path), "doctor"])

    assert result.exit_code == 0
    assert "[ok] config:" in result.output
    assert "[ok] shell: zsh" in result.output
    assert "[ok] conda: /fake/conda.sh" in result.output
    assert "[ok] ssh: /fake/ssh" in result.output
    assert "[ok] rsync: /fake/rsync" in result.output


def test_doctor_fails_for_missing_configuration(tmp_path: Path) -> None:
    config_path = tmp_path / "missing.toml"

    result = runner.invoke(app, ["--config", str(config_path), "doctor"])

    assert result.exit_code == 1
    assert "[error] config: configuration not found" in result.output


def test_doctor_reports_disabled_conda_initialization(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "schema_version = 1\n\n[shell]\ninitialize_conda = false\n",
        encoding="utf-8",
    )

    with (
        patch.dict("os.environ", {"SHELL": "/bin/zsh"}),
        patch("lab_env.diagnostics.find_conda_init", return_value=None),
        patch("lab_env.diagnostics.shutil.which", side_effect=lambda name: f"/fake/{name}"),
    ):
        result = runner.invoke(app, ["--config", str(config_path), "doctor"])

    assert result.exit_code == 0
    assert "[ok] conda: initialization disabled in config" in result.output


def test_shell_cli_preview_install_status_and_uninstall(tmp_path: Path) -> None:
    config_path = tmp_path / "config" / "config.toml"
    config_path.parent.mkdir()
    config_path.write_text("schema_version = 1\n[hosts]\n", encoding="utf-8")
    rc_path = tmp_path / "home" / ".zshrc"
    rc_path.parent.mkdir()
    rc_path.write_text("export EXISTING=value\n", encoding="utf-8")
    common_args = [
        "--config",
        str(config_path),
        "shell",
    ]
    shell_args = ["--shell", "zsh", "--rc", str(rc_path)]

    preview_result = runner.invoke(app, [*common_args, "preview", *shell_args])
    install_result = runner.invoke(app, [*common_args, "install", *shell_args])
    status_result = runner.invoke(app, [*common_args, "status", *shell_args])
    uninstall_result = runner.invoke(app, [*common_args, "uninstall", *shell_args])

    assert preview_result.exit_code == 0
    assert "managed startup block" in preview_result.output
    assert install_result.exit_code == 0
    assert "backup:" in install_result.output
    assert "zsh: installed" in status_result.output
    assert uninstall_result.exit_code == 0
    assert rc_path.read_text(encoding="utf-8") == "export EXISTING=value\n"
