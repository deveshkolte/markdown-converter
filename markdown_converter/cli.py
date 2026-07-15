"""CLI entry point — subcommands for file, folder, pipeline, rag, benchmark.

Preserves backward compatibility: ``mdconvert <file>`` still works as before
(no subcommand required for single-file conversion).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from .benchmark import run_benchmark
from .converter import convert
from .logger import get_logger, set_level
from .pipeline import run_pipeline_to_json
from .utils import find_files, output_path_for, validate_input_file

try:
    from rich.console import Console

    HAS_RICH = True
    console = Console()
except ImportError:
    HAS_RICH = False
    console = None

try:
    from tqdm import tqdm

    HAS_TQDM = True
except ImportError:
    HAS_TQDM = False


# ── Parser construction ──────────────────────────────────────────────────────


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mdconvert",
        description="Convert documents to Markdown and preprocess for AI.",
        epilog="See 'mdconvert <command> --help' for command-specific help.",
    )

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug-level logging",
    )

    sub = parser.add_subparsers(dest="command")

    # ── file ──────────────────────────────────────────────────────────────
    p_file = sub.add_parser("file", help="Convert a single document to Markdown")
    p_file.add_argument("input", type=str, help="Path to the document")
    p_file.add_argument("-o", "--output", type=str, default=None, help="Output directory")
    p_file.add_argument("--overwrite", action="store_true", help="Overwrite existing .md")

    # ── folder ────────────────────────────────────────────────────────────
    p_folder = sub.add_parser("folder", help="Convert all documents in a directory")
    p_folder.add_argument("input", type=str, help="Directory to scan")
    p_folder.add_argument("-o", "--output", type=str, default=None, help="Output directory")
    p_folder.add_argument("--recursive", action="store_true", help="Scan subdirectories")
    p_folder.add_argument("--overwrite", action="store_true", help="Overwrite existing .md")

    # ── pipeline ──────────────────────────────────────────────────────────
    p_pipe = sub.add_parser("pipeline", help="Full AI preprocessing pipeline")
    p_pipe.add_argument("input", type=str, help="Document to process")
    p_pipe.add_argument("-o", "--output", type=str, default=None, help="Output JSON path")
    p_pipe.add_argument(
        "--chunk-strategy",
        default="recursive",
        choices=["fixed", "recursive", "semantic"],
        help="Chunking strategy (default: recursive)",
    )
    p_pipe.add_argument("--chunk-size", type=int, default=1000, help="Chunk size in chars")
    p_pipe.add_argument("--chunk-overlap", type=int, default=200, help="Chunk overlap in chars")

    # ── rag ───────────────────────────────────────────────────────────────
    p_rag = sub.add_parser("rag", help="Ask questions about a document (RAG)")
    p_rag.add_argument("input", type=str, help="Document to ingest and query")
    p_rag.add_argument(
        "question",
        type=str,
        nargs="?",
        default=None,
        help="Question to ask (omit for interactive mode)",
    )
    p_rag.add_argument(
        "--model",
        default="openai/gpt-4o-mini",
        help="OpenRouter model (default: openai/gpt-4o-mini)",
    )
    p_rag.add_argument(
        "--chunk-strategy", default="recursive", choices=["fixed", "recursive", "semantic"]
    )
    p_rag.add_argument("--chunk-size", type=int, default=1000)
    p_rag.add_argument("--chunk-overlap", type=int, default=200)

    # ── benchmark ─────────────────────────────────────────────────────────
    p_bench = sub.add_parser("benchmark", help="Benchmark conversion performance")
    p_bench.add_argument("input", type=str, help="Directory with test documents")
    p_bench.add_argument("--iterations", type=int, default=1, help="Number of benchmark rounds")

    return parser


# ── Legacy parser (backward compat) ──────────────────────────────────────────


def build_legacy_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="mdconvert",
        description="Convert a document to Markdown (legacy mode).",
    )
    parser.add_argument("input", type=str, help="Path to the document")
    parser.add_argument("-o", "--output", type=str, default=None, help="Output directory")
    parser.add_argument("-v", "--verbose", action="store_true", help="Enable debug logging")
    parser.add_argument("--overwrite", action="store_true", help="Overwrite existing .md")
    return parser


# ── Command handlers ─────────────────────────────────────────────────────────


def _setup(args: argparse.Namespace) -> Any:
    """Configure logging and return a logger."""
    if getattr(args, "verbose", False):
        set_level("DEBUG")
    return get_logger()


def _print(text: str, style: str = "green") -> None:
    """Print with optional rich styling."""
    if HAS_RICH:
        console.print(f"[{style}]{text}[/{style}]")
    else:
        print(text)


def handle_file(args: argparse.Namespace, logger: Any) -> int:
    """Convert a single file."""
    try:
        input_path = validate_input_file(args.input)
    except (FileNotFoundError, IsADirectoryError) as exc:
        logger.error(str(exc))
        return 1

    output_path = output_path_for(input_path, args.output)
    logger.debug("Output: %s", output_path)

    if output_path.exists() and not args.overwrite:
        _print(f"⏭ Skipped (exists): {output_path}", "yellow")
        return 0

    try:
        markdown = convert(input_path)
    except Exception as exc:
        logger.exception("Conversion failed: %s", exc)
        return 1

    try:
        output_path.write_text(markdown, encoding="utf-8")
    except OSError as exc:
        logger.exception("Write failed: %s", exc)
        return 1

    _print(f"✔ Saved {output_path.name} → {output_path.parent}", "green")
    return 0


def handle_folder(args: argparse.Namespace, logger: Any) -> int:
    """Convert all supported files in a directory."""
    input_dir = Path(args.input)
    if not input_dir.is_dir():
        logger.error("Directory not found: %s", input_dir)
        return 1

    files = find_files(input_dir, recursive=args.recursive)
    if not files:
        _print("No supported files found.", "yellow")
        return 0

    converted = 0
    skipped = 0
    failed = 0

    iterator = tqdm(files, desc="Converting", unit="file") if HAS_TQDM else files

    for file_path in iterator:
        output_path = output_path_for(file_path, args.output)

        if output_path.exists() and not args.overwrite:
            skipped += 1
            continue

        try:
            markdown = convert(file_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text(markdown, encoding="utf-8")
            converted += 1
        except Exception:
            failed += 1

        if HAS_TQDM:
            iterator.set_postfix(ok=converted, skip=skipped, fail=failed)

    _print(f"✔ {converted} converted, {skipped} skipped, {failed} failed", "green")
    return 1 if failed else 0


def handle_pipeline(args: argparse.Namespace, logger: Any) -> int:
    """Run the full AI preprocessing pipeline."""
    try:
        _ = validate_input_file(args.input)
    except (FileNotFoundError, IsADirectoryError) as exc:
        logger.error(str(exc))
        return 1

    try:
        json_str = run_pipeline_to_json(
            args.input,
            output_path=args.output,
            chunk_strategy=args.chunk_strategy,
            chunk_size=args.chunk_size,
            chunk_overlap=args.chunk_overlap,
        )
        if not args.output:
            print(json_str)
        else:
            _print(f"✔ Pipeline output → {args.output}", "green")
    except Exception as exc:
        logger.exception("Pipeline failed: %s", exc)
        return 1

    return 0


def handle_rag(args: argparse.Namespace, logger: Any) -> int:
    """Ingest a document and answer questions about it."""
    import os

    if not os.environ.get("OPENROUTER_API_KEY"):
        logger.error(
            "OPENROUTER_API_KEY environment variable is not set.\n"
            "Get a key at https://openrouter.ai/keys"
        )
        return 1

    try:
        _ = validate_input_file(args.input)
    except (FileNotFoundError, IsADirectoryError) as exc:
        logger.error(str(exc))
        return 1

    # Ingest
    _print(f"Ingesting {Path(args.input).name} …", "cyan")
    from .rag import ingest_document

    summary = ingest_document(
        args.input,
        chunk_strategy=args.chunk_strategy,
        chunk_size=args.chunk_size,
        chunk_overlap=args.chunk_overlap,
    )
    _print(f"Ingested {summary['chunks_added']} chunks", "green")

    # Question
    if args.question:
        questions = [args.question]
    else:
        _print("Entering interactive mode. Type 'quit' to exit.", "cyan")
        questions = []
        while True:
            try:
                q = input("\n❓ ").strip()
                if q.lower() in ("quit", "exit", ""):
                    break
                questions.append(q)
            except (EOFError, KeyboardInterrupt):
                break

    from .rag import ask_document

    for q in questions:
        _print(f"\n❓ {q}", "bold cyan")
        result = ask_document(
            q,
            document_path=args.input,
            model=args.model,
        )
        print(result["answer"])

    return 0


def handle_benchmark(args: argparse.Namespace) -> int:
    """Benchmark conversion performance."""
    results = run_benchmark(args.input, iterations=args.iterations)

    if results["files_found"] == 0:
        _print(results["table"], "yellow")
        return 0

    _print(f"\nBenchmarked {results['files_found']} files", "cyan")
    print(results["table"])
    return 0


# ── Main dispatch ────────────────────────────────────────────────────────────


def main(argv: list[str] | None = None) -> int:
    """CLI entry point.

    Detects whether a subcommand or legacy positional was given and dispatches
    to the appropriate handler.
    """
    if argv is None:
        argv = sys.argv[1:]

    # Detect subcommand or legacy mode
    if argv and argv[0] in ("file", "folder", "pipeline", "rag", "benchmark"):
        parser = build_parser()
        args = parser.parse_args(argv)
        mode = args.command
    else:
        parser = build_legacy_parser()
        args = parser.parse_args(argv)
        mode = "legacy"

    logger = _setup(args)

    try:
        if mode == "legacy" or mode == "file":
            return handle_file(args, logger)
        elif mode == "folder":
            return handle_folder(args, logger)
        elif mode == "pipeline":
            return handle_pipeline(args, logger)
        elif mode == "rag":
            return handle_rag(args, logger)
        elif mode == "benchmark":
            return handle_benchmark(args)
        else:
            logger.error("Unknown command: %s", mode)
            return 1
    except KeyboardInterrupt:
        _print("\nInterrupted.", "yellow")
        return 130


if __name__ == "__main__":
    sys.exit(main())
