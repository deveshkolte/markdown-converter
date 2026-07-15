"""Unit tests for the markdown_converter package."""

from pathlib import Path

import pytest

from markdown_converter.utils import output_path_for, validate_input_file


class TestValidateInputFile:
    def test_missing_file_raises(self, tmp_path: Path) -> None:
        missing = tmp_path / "does_not_exist.pdf"
        with pytest.raises(FileNotFoundError, match="input file not found"):
            validate_input_file(missing)

    def test_directory_raises(self, tmp_path: Path) -> None:
        with pytest.raises(IsADirectoryError, match="expected a file"):
            validate_input_file(tmp_path)

    def test_valid_file_returns_resolved_path(self, tmp_path: Path) -> None:
        f = tmp_path / "test.pdf"
        f.write_text("dummy content")
        result = validate_input_file(f)
        assert result == f.resolve()
        assert result.is_absolute()


class TestOutputPathFor:
    def test_default_same_directory(self, tmp_path: Path) -> None:
        inp = tmp_path / "report.pdf"
        out = output_path_for(inp)
        assert out == tmp_path / "report.md"

    def test_with_output_dir(self, tmp_path: Path) -> None:
        inp = tmp_path / "report.pdf"
        out_dir = tmp_path / "out"
        out = output_path_for(inp, out_dir)
        assert out == out_dir / "report.md"
        assert out_dir.exists()

    def test_with_relative_output_dir(self, tmp_path: Path) -> None:
        inp = tmp_path / "report.pdf"
        out = output_path_for(inp, "relative_out")
        assert out.name == "report.md"
        assert out.parent.exists()


class TestCliIntegration:
    """Smoke-test that the CLI runs end-to-end."""

    def test_help_succeeds(self) -> None:
        from markdown_converter.cli import main

        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0

    def test_missing_input_returns_error(self) -> None:
        from markdown_converter.cli import main

        assert main(["/nonexistent/path.pdf"]) == 1
