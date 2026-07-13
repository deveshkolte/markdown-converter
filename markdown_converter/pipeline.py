"""End-to-end document preprocessing pipeline.

Converts a document to Markdown, chunks it, extracts metadata, and returns a
structured :class:`Document` ready for embedding or serialisation.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from .chunking import Chunker, get_chunker
from .converter import convert
from .logger import get_logger
from .models import Chunk, Document, DocumentMetadata
from .worker import cached

logger = get_logger()


@cached  # disk-cache the full pipeline output
def run_pipeline(
    input_path: str | Path,
    chunk_strategy: str = "recursive",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> Document:
    """Run the full preprocessing pipeline on a single document.

    Steps:

    1. Convert the document to Markdown via MarkItDown.
    2. Count words and characters.
    3. Extract basic metadata (title, file type, size).
    4. Chunk the markdown text using the requested strategy.
    5. Return a :class:`Document` with all fields populated.

    Args:
        input_path: Path to the source document.
        chunk_strategy: One of ``"fixed"``, ``"recursive"``, ``"semantic"``.
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlap between adjacent chunks (fixed/recursive only).

    Returns:
        A fully populated :class:`Document`.
    """
    path = Path(input_path).resolve()

    logger.info("Pipeline: converting %s …", path.name)
    markdown = convert(path)

    word_count = len(markdown.split())
    char_count = len(markdown)

    metadata = DocumentMetadata(
        title=path.stem,
        file_type=path.suffix.lstrip(".").lower(),
        file_path=path,
        file_size_bytes=os.path.getsize(path),
        word_count=word_count,
        char_count=char_count,
    )

    logger.info(
        "Pipeline: chunking %s (%s strategy) …",
        path.name,
        chunk_strategy,
    )
    chunker: Chunker = get_chunker(chunk_strategy, chunk_size, chunk_overlap)
    chunks: list[Chunk] = chunker.chunk(markdown, source=path.name)
    metadata.chunk_count = len(chunks)

    logger.info("Pipeline: done — %d chunks created", len(chunks))

    return Document(markdown=markdown, metadata=metadata, chunks=chunks)


def run_pipeline_to_json(
    input_path: str | Path,
    output_path: str | Path | None = None,
    **kwargs: Any,
) -> str:
    """Run the pipeline and return (or save) the result as JSON.

    Args:
        input_path: Path to the source document.
        output_path: If given, write JSON to this file.
        **kwargs: Passed through to :func:`run_pipeline`.

    Returns:
        The JSON string.
    """
    doc = run_pipeline(input_path, **kwargs)
    data = doc.to_dict()
    json_str = json.dumps(data, indent=2, default=str)

    if output_path:
        out = Path(output_path)
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(json_str, encoding="utf-8")
        logger.info("Pipeline output saved to %s", out)

    return json_str
