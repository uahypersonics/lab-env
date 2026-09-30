"""Tecplot batch-export tests."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from lab_env.tecplot import export_layouts


def test_export_layout_defaults_to_png_width_2000(tmp_path: Path) -> None:
    """Default exports must retain the convenient lay2pic behavior."""

    layout_path = tmp_path / "figure.lay"
    layout_path.write_text("layout", encoding="utf-8")
    tecplot_path = tmp_path / "tec360"
    tecplot_path.write_text("executable", encoding="utf-8")

    def fake_run(command, *, cwd, check):
        macro_path = Path(command[-1])
        macro_text = macro_path.read_text(encoding="utf-8")
        assert "EXPORTFORMAT = PNG" in macro_text
        assert "IMAGEWIDTH = 2000" in macro_text
        assert cwd == tmp_path
        assert check is True
        (tmp_path / "figure.png").write_bytes(b"png")

    with patch("lab_env.tecplot.export.subprocess.run", side_effect=fake_run) as mock_run:
        files = export_layouts([layout_path], tecplot_executable=tecplot_path)

    assert files == [tmp_path / "figure.png"]
    assert mock_run.call_count == 1


def test_export_layout_rejects_python_file(tmp_path: Path) -> None:
    """The compatibility command accepts Tecplot layouts, not Python files."""

    python_path = tmp_path / "figure.py"
    python_path.write_text("pass\n", encoding="utf-8")

    try:
        export_layouts([python_path], tecplot_executable=tmp_path / "tec360")
    except ValueError as exc:
        message = str(exc)
    else:
        raise AssertionError("expected ValueError")

    assert "layout must use .lay or .lpk" in message
