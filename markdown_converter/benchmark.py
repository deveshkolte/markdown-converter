"""Benchmarking utilities that measure and compare conversion strategies.

Provides both the core timing logic and a pretty-printed summary table.
"""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

from .logger import get_logger
from .utils import find_files
from .worker import benchmark_conversion

try:
    from rich.console import Console
    from rich.table import Table

    HAS_RICH = True
except ImportError:
    HAS_RICH = False

logger = get_logger()


def run_benchmark(
    directory: str | Path,
    iterations: int = 1,
) -> dict[str, Any]:
    """Run the full benchmark suite on all supported files in *directory*.

    Args:
        directory: Path containing documents to benchmark with.
        iterations: Number of runs per strategy.

    Returns:
        A dict with raw timings and a formatted table string.
    """
    path = Path(directory).resolve()
    files = find_files(path, recursive=True)

    if not files:
        logger.warning("No supported files found in %s", path)
        return {"files_found": 0, "table": "No files to benchmark."}

    logger.info(
        "Benchmarking with %d files (%d iteration(s)) …",
        len(files),
        iterations,
    )

    timings = benchmark_conversion(files, iterations=iterations)
    baseline = timings["sequential"]

    rows: list[tuple[str, float, float]] = []
    for method in ["sequential", "threaded", "multiprocess"]:
        t = timings[method]
        speedup = baseline / t if t > 0 else 1.0
        rows.append((method.capitalize(), t, speedup))

    table_str = _format_table(rows)

    return {
        "files_found": len(files),
        "timings": timings,
        "table": table_str,
    }


def _format_table(rows: list[tuple[str, float, float]]) -> str:
    """Return a rich table (or plain-text fallback) of benchmark results."""
    if HAS_RICH:
        console = Console()
        table = Table(title="Benchmark Results")
        table.add_column("Method", style="cyan")
        table.add_column("Duration", justify="right")
        table.add_column("Speed-up", justify="right")
        for name, duration, speedup in rows:
            table.add_row(name, f"{duration:.2f}s", f"{speedup:.2f}x")
        console.print(table)
        # Also return a string version
        out = f"Benchmark: {rows[0][1]:.2f}s sequential → {rows[1][1]:.2f}s threaded → {rows[2][1]:.2f}s multiprocess"
        return out
    else:
        lines = [f"{'Method':<20} {'Duration':>10} {'Speed-up':>10}"]
        lines.append("-" * 42)
        for name, duration, speedup in rows:
            lines.append(f"{name:<20} {duration:>8.2f}s {speedup:>8.2f}x")
        return "\n".join(lines)
