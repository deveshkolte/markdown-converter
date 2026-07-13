import os
from pathlib import Path
from typing import Optional


def resolve_path(path: str) -> Path:
    """Expand ``~``, environment variables, and return an absolute :class:`Path`.

    Args:
        path: A user-provided file or directory path.

    Returns:
        An absolute :class:`Path` with all expansions applied.
    """
    return Path(os.path.expanduser(os.path.expandvars(path))).resolve()


def validate_input_file(path: str | Path) -> Path:
    """Verify *path* exists, is a file, and return its absolute, resolved form.

    Args:
        path: The candidate input path.

    Returns:
        The resolved absolute :class:`Path`.

    Raises:
        FileNotFoundError: If the path does not exist.
        IsADirectoryError: If the path is a directory, not a file.
    """
    p = resolve_path(str(path)) if isinstance(path, str) else path.resolve()

    if not p.exists():
        raise FileNotFoundError(f"input file not found: {p}")
    if not p.is_file():
        raise IsADirectoryError(f"expected a file, got a directory: {p}")

    return p


def output_path_for(input_path: Path, output_dir: Optional[str | Path] = None) -> Path:
    """Derive the ``.md`` output path for a given input file.

    * Without *output_dir*: same directory as the input, same stem, ``.md`` suffix.
    * With *output_dir*: placed inside *output_dir* with the input's stem and
      ``.md`` suffix.  The directory is created if it does not exist.

    Args:
        input_path: The resolved input file path.
        output_dir: Optional alternative output directory.

    Returns:
        The output :class:`Path`.
    """
    if output_dir is not None:
        out_dir = resolve_path(str(output_dir))
        out_dir.mkdir(parents=True, exist_ok=True)
        return out_dir / f"{input_path.stem}.md"

    return input_path.with_suffix(".md")


def find_files(directory: Path, recursive: bool = False) -> list[Path]:
    """Discover all supported document files in *directory*.

    Args:
        directory: The directory to scan.
        recursive: If ``True``, descend into subdirectories.

    Returns:
        A sorted list of file paths with supported extensions.
    """
    exts = supported_extensions()
    if recursive:
        return sorted(
            p for p in directory.rglob("*")
            if p.is_file() and p.suffix.lower() in exts
        )
    return sorted(
        p for p in directory.glob("*")
        if p.is_file() and p.suffix.lower() in exts
    )


def supported_extensions() -> list[str]:
    """Return the list of file extensions MarkItDown can handle."""
    return [
        ".pdf",
        ".docx",
        ".pptx",
        ".xlsx",
        ".csv",
        ".html",
        ".htm",
        ".txt",
        ".md",
        ".epub",
        ".zip",
        ".msg",
        ".ipynb",
        ".jpg",
        ".jpeg",
        ".png",
        ".gif",
        ".bmp",
        ".svg",
        ".mp3",
        ".wav",
        ".m4a",
        ".flac",
    ]
