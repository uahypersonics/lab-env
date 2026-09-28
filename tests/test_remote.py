"""Remote command construction and CLI tests."""

from __future__ import annotations

from os.path import expanduser
from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from lab_env.cli import app
from lab_env.hosts.models import HostConfig
from lab_env.remote import build_connect_command, build_transfer_command

runner = CliRunner()


def test_build_connect_command_preserves_argument_boundaries() -> None:
    host = HostConfig(destination="cluster-alias", ssh_command="/opt/ossh/bin/ssh")

    command = build_connect_command(host, ["printf", "hello world"])

    assert command == [
        "/opt/ossh/bin/ssh",
        "cluster-alias",
        "printf",
        "hello world",
    ]


def test_build_transfer_commands_are_resumable() -> None:
    host = HostConfig(destination="cluster-alias")

    pull_command = build_transfer_command("pull", host, "results/run 1/", "~/data")
    push_command = build_transfer_command("push", host, "~/input", "/scratch/run 1/")

    assert "--partial" in pull_command
    assert "--append-verify" in pull_command
    assert pull_command[-2:] == ["cluster-alias:results/run 1/", expanduser("~/data")]
    assert push_command[-2:] == [expanduser("~/input"), "cluster-alias:/scratch/run 1/"]


def test_remote_cli_dry_run_uses_configured_host(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        "schema_version = 1\n\n"
        "[hosts.cluster]\n"
        'destination = "cluster-alias"\n'
        'ssh_command = "/opt/ossh/bin/ssh"\n',
        encoding="utf-8",
    )

    connect_result = runner.invoke(
        app,
        ["--config", str(config_path), "connect", "cluster", "--dry-run"],
    )
    pull_result = runner.invoke(
        app,
        ["--config", str(config_path), "pull", "cluster", "results/", ".", "--dry-run"],
    )

    assert connect_result.exit_code == 0
    assert connect_result.output.strip() == "/opt/ossh/bin/ssh cluster-alias"
    assert pull_result.exit_code == 0
    assert "--rsh /opt/ossh/bin/ssh" in pull_result.output
    assert "cluster-alias:results/" in pull_result.output


def test_remote_cli_runs_without_a_shell_and_preserves_exit_code(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text(
        'schema_version = 1\n\n[hosts.cluster]\ndestination = "cluster-alias"\n',
        encoding="utf-8",
    )

    with patch("lab_env.remote.subprocess.run") as run_process:
        run_process.return_value.returncode = 23
        result = runner.invoke(
            app,
            ["--config", str(config_path), "push", "cluster", "input/", "work/"],
        )

    assert result.exit_code == 23
    run_process.assert_called_once()
    assert run_process.call_args.kwargs == {"check": False}
    assert run_process.call_args.args[0][-2:] == ("input/", "cluster-alias:work/")


def test_remote_cli_rejects_unknown_host(tmp_path: Path) -> None:
    config_path = tmp_path / "config.toml"
    config_path.write_text("schema_version = 1\n[hosts]\n", encoding="utf-8")

    result = runner.invoke(
        app,
        ["--config", str(config_path), "connect", "missing", "--dry-run"],
    )

    assert result.exit_code == 2
    assert "unknown host 'missing'" in result.output
