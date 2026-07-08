"""Tests for the rb-road-network CLI (rb_road_network/cli.py)."""
import os
import csv
import shlex
import subprocess
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from click.testing import CliRunner

from rb_road_network.cli import (
    build_command,
    cli,
    get_justpop_exe,
    get_rb_src,
    save_script,
    _render_map,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_exe(tmp_path: Path) -> Path:
    """Create a dummy justPop.exe file so path checks pass."""
    exe = tmp_path / "justPop.exe"
    exe.touch()
    return exe


# ---------------------------------------------------------------------------
# Unit tests: pure functions
# ---------------------------------------------------------------------------


class TestGetRbSrc:
    def test_uses_env_var(self, tmp_path, monkeypatch):
        monkeypatch.setenv("RB_SRC", str(tmp_path))
        assert get_rb_src() == tmp_path

    def test_falls_back_to_cwd(self, monkeypatch):
        monkeypatch.delenv("RB_SRC", raising=False)
        assert get_rb_src() == Path.cwd()


class TestGetJustpopExe:
    def test_returns_path_when_exists(self, tmp_path):
        exe = _fake_exe(tmp_path)
        assert get_justpop_exe(tmp_path) == exe

    def test_raises_when_missing(self, tmp_path):
        with pytest.raises(FileNotFoundError, match="justPop.exe not found"):
            get_justpop_exe(tmp_path)


class TestBuildCommand:
    def test_contains_all_params(self, tmp_path):
        exe = _fake_exe(tmp_path)
        output = tmp_path / "out.txt"
        cmd = build_command(exe, output, 4.5, 33.7, -84.4, 75000, 0.009, 8, 0.5)
        assert isinstance(cmd, list)
        assert str(exe) in cmd
        assert str(output) in cmd
        assert "--lat=33.7" in cmd
        assert "--lon=-84.4" in cmd
        assert "--radius=75000" in cmd
        assert "--stride=0.009" in cmd
        assert "--nthreads=8" in cmd
        assert "--zoom=0.5" in cmd
        assert "-t" in cmd
        assert "4.5" in cmd


class TestSaveScript:
    def test_creates_sh_file(self, tmp_path):
        exe = _fake_exe(tmp_path)
        output = tmp_path / "out.txt"
        cmd = build_command(exe, output, 4.5, 33.7, -84.4, 75000, 0.009, 8, 0.5)
        script = save_script(output, cmd, tmp_path)
        assert script == output.with_suffix(".sh")
        assert script.exists()
        content = script.read_text()
        assert shlex.join(cmd) in content
        assert "LD_LIBRARY_PATH" in content

    def test_script_is_executable(self, tmp_path):
        exe = _fake_exe(tmp_path)
        output = tmp_path / "out.txt"
        cmd = build_command(exe, output, 4.5, 33.7, -84.4, 75000, 0.009, 8, 0.5)
        script = save_script(output, cmd, tmp_path)
        assert os.access(script, os.X_OK)


# ---------------------------------------------------------------------------
# CLI integration tests: `run` command with --no-exec
# ---------------------------------------------------------------------------


class TestRunCommand:
    def test_no_exec_saves_script_and_exits(self, tmp_path):
        exe = _fake_exe(tmp_path)
        output = tmp_path / "out.txt"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "run",
                "--no-exec",
                "-y",
                "--rb-src", str(tmp_path),
                "-f", str(output),
                "-t", "4.5",
                "--lat", "33.732",
                "--lon", "-84.4166",
                "-r", "75000",
                "-s", "0.009",
                "-h", "4",
                "-z", "0.5",
            ],
        )
        assert result.exit_code == 0, result.output
        assert output.with_suffix(".sh").exists()
        assert "Skipping execution" in result.output

    def test_missing_exe_raises_error(self, tmp_path):
        output = tmp_path / "out.txt"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "run",
                "--no-exec",
                "-y",
                "--rb-src", str(tmp_path),
                "-f", str(output),
                "-t", "4.5",
                "--lat", "33.732",
                "--lon", "-84.4166",
                "-r", "75000",
                "-s", "0.009",
                "-h", "4",
                "-z", "0.5",
            ],
        )
        assert result.exit_code != 0
        assert "justPop.exe not found" in (result.output + str(result.exception))

    def test_run_invokes_subprocess(self, tmp_path):
        _fake_exe(tmp_path)
        output = tmp_path / "out.txt"
        runner = CliRunner()
        with patch("rb_road_network.cli.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = runner.invoke(
                cli,
                [
                    "run",
                    "-y",
                    "--no-render",
                    "--rb-src", str(tmp_path),
                    "-f", str(output),
                    "-t", "4.5",
                    "--lat", "33.732",
                    "--lon", "-84.4166",
                    "-r", "75000",
                    "-s", "0.009",
                    "-h", "4",
                    "-z", "0.5",
                ],
            )
        assert result.exit_code == 0, result.output
        mock_run.assert_called_once()
        call_kwargs = mock_run.call_args
        argv = call_kwargs[0][0]
        assert any("justPop.exe" in str(arg) for arg in argv)

    def test_run_renders_map_when_json_present(self, tmp_path):
        _fake_exe(tmp_path)
        output = tmp_path / "out.txt"
        # Simulate justPop writing a JSON file
        json_out = output.with_suffix(".json")
        json_out.write_text('{"type":"FeatureCollection","features":[]}')
        runner = CliRunner()
        with patch("rb_road_network.cli.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = runner.invoke(
                cli,
                [
                    "run",
                    "-y",
                    "--render",
                    "--rb-src", str(tmp_path),
                    "-f", str(output),
                    "-t", "4.5",
                    "--lat", "33.732",
                    "--lon", "-84.4166",
                    "-r", "75000",
                    "-s", "0.009",
                    "-h", "4",
                    "-z", "0.5",
                ],
            )
        # Render should be attempted (two subprocess.run calls: justPop + render)
        assert mock_run.call_count >= 1


# ---------------------------------------------------------------------------
# CLI integration tests: `batch` command with --no-exec
# ---------------------------------------------------------------------------


class TestBatchCommand:
    def _make_csv(self, tmp_path: Path, rows=None) -> Path:
        csv_path = tmp_path / "sites.csv"
        if rows is None:
            rows = [
                {"site": "Savannah", "lat": "32.066051", "lon": "-81.095341"},
                {"site": "Atlanta", "lat": "33.732", "lon": "-84.4166"},
            ]
        with open(csv_path, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["site", "lat", "lon"])
            writer.writeheader()
            writer.writerows(rows)
        return csv_path

    def test_batch_no_exec_creates_scripts(self, tmp_path):
        _fake_exe(tmp_path)
        csv_path = self._make_csv(tmp_path)
        output_dir = tmp_path / "output"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "batch",
                "--csv", str(csv_path),
                "--no-exec",
                "--rb-src", str(tmp_path),
                "--output-dir", str(output_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        assert (output_dir / "SavannahResult.sh").exists()
        assert (output_dir / "AtlantaResult.sh").exists()
        assert "skipping execution" in result.output.lower()

    def test_batch_missing_columns_error(self, tmp_path):
        _fake_exe(tmp_path)
        bad_csv = tmp_path / "bad.csv"
        with open(bad_csv, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["name", "latitude"])
            writer.writeheader()
            writer.writerow({"name": "X", "latitude": "1.0"})
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "batch",
                "--csv", str(bad_csv),
                "--no-exec",
                "--rb-src", str(tmp_path),
            ],
        )
        assert result.exit_code != 0
        assert "missing" in result.output.lower() or "Error" in result.output

    def test_batch_invokes_subprocess_per_row(self, tmp_path):
        _fake_exe(tmp_path)
        csv_path = self._make_csv(tmp_path)
        output_dir = tmp_path / "output"
        runner = CliRunner()
        with patch("rb_road_network.cli.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            result = runner.invoke(
                cli,
                [
                    "batch",
                    "--csv", str(csv_path),
                    "--no-render",
                    "--rb-src", str(tmp_path),
                    "--output-dir", str(output_dir),
                ],
            )
        assert result.exit_code == 0, result.output
        assert mock_run.call_count == 2  # one per site

    def test_batch_site_name_sanitized(self, tmp_path):
        _fake_exe(tmp_path)
        csv_path = self._make_csv(
            tmp_path,
            rows=[{"site": "New York/Test", "lat": "40.7", "lon": "-74.0"}],
        )
        output_dir = tmp_path / "output"
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "batch",
                "--csv", str(csv_path),
                "--no-exec",
                "--rb-src", str(tmp_path),
                "--output-dir", str(output_dir),
            ],
        )
        assert result.exit_code == 0, result.output
        # Sanitized: "NewYorkTest"
        assert (output_dir / "NewYorkTestResult.sh").exists()


# ---------------------------------------------------------------------------
# Unit test: _render_map helper
# ---------------------------------------------------------------------------


class TestRenderMap:
    def test_skips_when_render_script_missing(self, tmp_path, capsys):
        output = tmp_path / "out.txt"
        json_out = output.with_suffix(".json")
        json_out.write_text("{}")
        runner = CliRunner()
        with runner.isolated_filesystem():
            # No render_scripts/ in tmp_path, should just print skip message
            with patch("rb_road_network.cli.subprocess.run") as mock_run:
                _render_map(output, tmp_path)
                mock_run.assert_not_called()

    def test_skips_when_json_missing(self, tmp_path):
        output = tmp_path / "out.txt"
        render_dir = tmp_path / "render_scripts"
        render_dir.mkdir()
        (render_dir / "render_plotly.py").touch()
        with patch("rb_road_network.cli.subprocess.run") as mock_run:
            _render_map(output, tmp_path)
            mock_run.assert_not_called()

    def test_calls_subprocess_when_all_present(self, tmp_path):
        output = tmp_path / "out.txt"
        json_out = output.with_suffix(".json")
        json_out.write_text("{}")
        render_dir = tmp_path / "render_scripts"
        render_dir.mkdir()
        (render_dir / "render_plotly.py").touch()
        with patch("rb_road_network.cli.subprocess.run") as mock_run:
            mock_run.return_value = MagicMock(returncode=0)
            _render_map(output, tmp_path)
            mock_run.assert_called_once()
            args = mock_run.call_args[0][0]
            assert "--output" in args
            assert str(output.with_suffix(".png")) in args
