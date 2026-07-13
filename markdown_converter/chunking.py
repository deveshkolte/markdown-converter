"""Text chunking strategies for splitting documents into manageable pieces.

Each strategy implements a ``chunk(text: str) -> list[Chunk]`` interface so
they are interchangeable and composable.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from typing import Any

from .models import Chunk


class Chunker(ABC):
    """Abstract base for all chunking strategies."""

    @abstractmethod
    def chunk(self, text: str, **metadata: Any) -> list[Chunk]:
        ...


class FixedSizeChunker(Chunker):
    """Split text into fixed-size character chunks with configurable overlap.

    This is the simplest strategy — useful when your embedding model has a
    fixed token limit.  The trade-off is that semantic boundaries (sentences,
    paragraphs) may be cut mid-way.

    Args:
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Number of overlapping characters between adjacent chunks.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk(self, text: str, **metadata: Any) -> list[Chunk]:
        chunks: list[Chunk] = []
        start = 0
        index = 0

        while start < len(text):
            end = min(start + self.chunk_size, len(text))
            chunk_text = text[start:end]
            chunks.append(
                Chunk.create(
                    chunk_text,
                    chunk_index=index,
                    char_start=start,
                    char_end=end,
                    strategy="fixed",
                    **metadata,
                )
            )
            index += 1
            if end == len(text):
                break
            start += self.chunk_size - self.chunk_overlap

        return chunks


class RecursiveChunker(Chunker):
    """Recursively split text by natural boundaries.

    Attempts to split at paragraph breaks first, then sentence boundaries,
    then falls back to character-level splitting.  This preserves semantic
    structure better than fixed-size chunking.

    The separators are tried in order:

    1. ``"\\n\\n"`` (paragraph break)
    2. ``"\\n"`` (line break)
    3. ``". "`` (sentence end)
    4. ``" "`` (word boundary)
    5. ``""`` (character — guaranteed to fit)

    Args:
        chunk_size: Maximum characters per chunk.
        chunk_overlap: Overlapping characters between chunks.
    """

    def __init__(self, chunk_size: int = 1000, chunk_overlap: int = 200) -> None:
        if chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self._separators = ["\n\n", "\n", ". ", " ", ""]

    def chunk(self, text: str, **metadata: Any) -> list[Chunk]:
        return self._chunk_recursive(text, self._separators, **metadata)

    def _chunk_recursive(
        self,
        text: str,
        separators: list[str],
        **metadata: Any,
    ) -> list[Chunk]:
        """Recursive splitting logic."""
        if len(text) <= self.chunk_size or not separators:
            return [Chunk.create(text, strategy="recursive", **metadata)]

        sep = separators[0]
        if sep == "":
            # Character-level fallback
            return self._split_fixed(text, **metadata)

        parts = text.split(sep)
        # If splitting with this separator doesn't help, try the next one
        if len(parts) == 1:
            return self._chunk_recursive(text, separators[1:], **metadata)

        chunks: list[Chunk] = []
        buffer = ""
        for part in parts:
            candidate = f"{buffer}{sep}{part}" if buffer else part
            if len(candidate) <= self.chunk_size:
                buffer = candidate
            else:
                if buffer:
                    chunks.append(
                        Chunk.create(buffer, strategy="recursive", **metadata)
                    )
                buffer = part

        if buffer:
            chunks.append(Chunk.create(buffer, strategy="recursive", **metadata))

        return chunks

    def _split_fixed(self, text: str, **metadata: Any) -> list[Chunk]:
        """Fallback: split at character level."""
        return FixedSizeChunker(self.chunk_size, self.chunk_overlap).chunk(
            text, **metadata
        )


class SemanticChunker(Chunker):
    """Split text at Markdown heading boundaries.

    This strategy preserves document structure by keeping each section
    (``# Heading`` → next heading) as its own chunk.  Subsections under
    a heading are grouped together as long as they stay under the size
    limit, otherwise they overflow into new chunks with the same section
    annotation.

    This is the best strategy for RAG on documents that have a clear
    heading hierarchy (reports, documentation, articles).

    Args:
        max_chunk_size: Hard character limit per chunk.  Sections longer
            than this are further split with the recursive strategy.
    """

    def __init__(self, max_chunk_size: int = 2000) -> None:
        self.max_chunk_size = max_chunk_size
        self._fallback = RecursiveChunker(
            chunk_size=max_chunk_size, chunk_overlap=100
        )
        self._heading_pattern = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)

    def chunk(self, text: str, **metadata: Any) -> list[Chunk]:
        sections = self._split_by_headings(text)
        chunks: list[Chunk] = []

        for section_heading, section_body in sections:
            section_text = (
                f"{section_heading}\n\n{section_body}" if section_heading else section_body
            )
            section_meta = {**metadata, "section": section_heading or "root"}

            if len(section_text) <= self.max_chunk_size:
                chunks.append(
                    Chunk.create(section_text, strategy="semantic", **section_meta)
                )
            else:
                # Oversized section — sub-chunk recursively
                sub_chunks = self._fallback._chunk_recursive(
                    section_text, self._fallback._separators, **section_meta
                )
                # Mark sub-chunks with their parent section
                for sc in sub_chunks:
                    sc.metadata["strategy"] = "semantic+recursive"
                chunks.extend(sub_chunks)

        return chunks

    def _split_by_headings(
        self, text: str
    ) -> list[tuple[str | None, str]]:
        """Split text at heading boundaries.

        Returns:
            A list of ``(heading, body)`` tuples.  The first entry may have
            ``None`` as heading (content before the first heading).
        """
        matches = list(self._heading_pattern.finditer(text))
        if not matches:
            return [(None, text)]

        sections: list[tuple[str | None, str]] = []
        prev_start = 0

        for i, match in enumerate(matches):
            heading = match.group(0).strip()
            start = match.start()
            if i > 0:
                prev_end = matches[i - 1].end()
                body = text[prev_end:start].strip()
                sections.append((matches[i - 1].group(0).strip(), body))
            elif start > 0:
                # Content before the first heading
                sections.append((None, text[prev_start:start].strip()))
            prev_start = start

        # Last section
        last_body = text[matches[-1].end() :].strip()
        sections.append((matches[-1].group(0).strip(), last_body))

        return sections


def get_chunker(
    strategy: str = "recursive",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> Chunker:
    """Factory: return a chunker by name."""
    strategy_map = {
        "fixed": FixedSizeChunker,
        "recursive": RecursiveChunker,
        "semantic": SemanticChunker,
    }
    cls = strategy_map.get(strategy)
    if cls is None:
        raise ValueError(
            f"Unknown chunking strategy {strategy!r}. "
            f"Choose from: {', '.join(strategy_map)}"
        )

    if strategy == "semantic":
        return cls(max_chunk_size=chunk_size)
    return cls(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
