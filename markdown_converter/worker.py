"""Concurrent processing, caching, and utility workers.

Optimisations implemented:

* **ThreadPoolExecutor** — ideal for I/O-bound work (MarkItDown conversion,
  API calls, file I/O).  Overlaps waiting time so total throughput increases
  nearly linearly with the number of files.
* **ProcessPoolExecutor** — useful for CPU-bound chunking of large texts.
  Bypasses the GIL so multiple cores are utilised.
* **Disk cache** — avoids re-converting files whose content hasn't changed.
  The cache key is ``(file_path, mtime, size)``, so edits invalidate the
  entry automatically.
"""

from __future__ import annotations

import functools
import hashlib
import os
import time
from concurrent.futures import Future, ProcessPoolExecutor, ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, TypeVar

from .logger import get_logger

logger = get_logger()

try:
    import diskcache

    _cache = diskcache.Cache(os.path.join(os.path.dirname(__file__), "..", ".cache"))
    HAS_DISKCACHE = True
except ImportError:
    _cache = None  # type: ignore[assignment]
    HAS_DISKCACHE = False

F = TypeVar("F", bound=Callable[..., Any])


def cached(func: F) -> F:
    """Decorator: disk-cache function results keyed by args + file mtime.

    The decorated function's first argument should be a file path (str or
    Path).  The cache invalidates when the file's modification time or size
    changes.

    This is a **read-through cache** — the first call is slow, subsequent
    calls with the same (unchanged) file are instant.
    """

    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        if not HAS_DISKCACHE:
            return func(*args, **kwargs)

        # Build cache key from the file path and its stat info
        path_arg = args[0] if args else kwargs.get("input_path")
        if path_arg is None:
            return func(*args, **kwargs)

        path = Path(path_arg).resolve()
        try:
            st = path.stat()
            raw_key = f"{path}|{st.st_mtime}|{st.st_size}|{func.__name__}"
        except OSError:
            return func(*args, **kwargs)

        key = hashlib.sha256(raw_key.encode()).hexdigest()
        if key in _cache:
            logger.debug("Cache hit for %s", path.name)
            return _cache[key]

        logger.debug("Cache miss for %s", path.name)
        result = func(*args, **kwargs)
        _cache[key] = result
        return result

    return wrapper  # type: ignore[return-value]


def convert_many_threaded(
    paths: list[Path],
    max_workers: int | None = None,
) -> dict[Path, str]:
    """Convert multiple files concurrently using a thread pool.

    Why threads instead of processes for MarkItDown?
    MarkItDown is I/O-bound (reading files, calling external converters).
    Threads are lightweight to create and share memory, so there is no
    serialisation overhead.  Python's GIL is not a bottleneck here because
    the worker threads spend most of their time waiting on I/O.

    Args:
        paths: List of file paths to convert.
        max_workers: Thread pool size (default: CPU count × 5).

    Returns:
        A dict mapping each input path to its markdown string.
    """
    results: dict[Path, str] = {}
    errors: list[tuple[Path, Exception]] = []

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        fut: dict[Future, Path] = {
            pool.submit(_convert_safe, p): p for p in paths
        }

        for future in as_completed(fut):
            p = fut[future]
            try:
                results[p] = future.result()
            except Exception as exc:
                errors.append((p, exc))
                logger.error("Failed to convert %s: %s", p.name, exc)

    if errors:
        logger.warning("%d/%d files failed", len(errors), len(paths))

    return results


def convert_many_parallel(
    paths: list[Path],
    max_workers: int | None = None,
) -> dict[Path, str]:
    """Convert multiple files using multiple processes.

    Useful when the conversion itself is CPU-heavy (e.g. OCR on images).
    Each process runs in its own Python interpreter, bypassing the GIL.

    The trade-off is higher memory usage and serialisation overhead for
    sending results back to the parent process.

    Args:
        paths: List of file paths to convert.
        max_workers: Process pool size (default: CPU count).

    Returns:
        A dict mapping each input path to its markdown string.
    """
    results: dict[Path, str] = {}

    with ProcessPoolExecutor(max_workers=max_workers) as pool:
        fut: dict[Future, Path] = {
            pool.submit(_convert_safe, p): p for p in paths
        }

        for future in as_completed(fut):
            p = fut[future]
            try:
                results[p] = future.result()
            except Exception as exc:
                logger.error("Failed to convert %s: %s", p.name, exc)

    return results


def _convert_safe(path: Path) -> str:
    """Thin wrapper around :func:`converter.convert` for use in pools."""
    from .converter import convert  # lazy import inside worker module

    return convert(path)


def benchmark_conversion(
    paths: list[Path],
    iterations: int = 1,
) -> dict[str, float]:
    """Benchmark sequential, threaded, and multiprocess conversion.

    Runs each method for *iterations* rounds and returns the **median**
    wall-clock time per method.  This gives a realistic picture of which
    strategy is fastest for your specific hardware and file set.

    Args:
        paths: List of files to use as the benchmark workload.
        iterations: Number of benchmark rounds per method.

    Returns:
        ``{"sequential": …, "threaded": …, "multiprocess": …}`` (seconds).
    """
    results: dict[str, list[float]] = {
        "sequential": [],
        "threaded": [],
        "multiprocess": [],
    }

    for _ in range(iterations):
        # Sequential
        start = time.perf_counter()
        for p in paths:
            _convert_safe(p)
        results["sequential"].append(time.perf_counter() - start)

        # Threaded
        start = time.perf_counter()
        convert_many_threaded(paths)
        results["threaded"].append(time.perf_counter() - start)

        # Multiprocess
        start = time.perf_counter()
        convert_many_parallel(paths)
        results["multiprocess"].append(time.perf_counter() - start)

    # Median across iterations
    medians = {
        k: sorted(v)[len(v) // 2] for k, v in results.items()
    }

    return medians
