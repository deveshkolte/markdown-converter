"""Data models for the document processing pipeline."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class Chunk:
    """A single chunk of text extracted from a document.

    Attributes:
        id: Unique identifier for the chunk (e.g. ``"chunk_0001"``).
        text: The chunk text content.
        metadata: Arbitrary metadata attached to this chunk
            (page number, section heading, token count, etc.).
        embedding: Optional vector embedding of the chunk text.
    """

    id: str
    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    embedding: list[float] | None = None

    @classmethod
    def create(cls, text: str, **metadata: Any) -> Chunk:
        """Factory method that auto-generates a unique ID."""
        return cls(
            id=f"chunk_{uuid.uuid4().hex[:12]}",
            text=text,
            metadata=metadata,
        )

    def __len__(self) -> int:
        return len(self.text)


@dataclass
class DocumentMetadata:
    """Metadata extracted from a source document.

    Attributes:
        title: Document title (filename stem if no title metadata exists).
        file_type: Lower-case file extension without dot (e.g. ``"pdf"``).
        file_path: Absolute path to the source file.
        file_size_bytes: Size of the source file in bytes.
        word_count: Total word count of the extracted markdown.
        char_count: Total character count of the extracted markdown.
        chunk_count: Number of chunks after processing.
        custom: Catch-all dict for format-specific metadata.
    """

    title: str
    file_type: str
    file_path: Path
    file_size_bytes: int
    word_count: int = 0
    char_count: int = 0
    chunk_count: int = 0
    custom: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "title": self.title,
            "file_type": self.file_type,
            "file_path": str(self.file_path),
            "file_size_bytes": self.file_size_bytes,
            "word_count": self.word_count,
            "char_count": self.char_count,
            "chunk_count": self.chunk_count,
        }
        if self.custom:
            result["custom"] = self.custom
        return result


@dataclass
class Document:
    """A fully processed document with its markdown, chunks, and metadata.

    This is the top-level output of the preprocessing pipeline.  It can be
    serialised to JSON for downstream use (RAG, training, etc.).

    Attributes:
        markdown: The full Markdown representation of the document.
        metadata: Structured metadata about the document.
        chunks: List of text chunks derived from the markdown.
    """

    markdown: str
    metadata: DocumentMetadata
    chunks: list[Chunk] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a JSON-compatible dictionary."""
        return {
            "title": self.metadata.title,
            "file_type": self.metadata.file_type,
            "file_path": str(self.metadata.file_path),
            "file_size_bytes": self.metadata.file_size_bytes,
            "word_count": self.metadata.word_count,
            "char_count": self.metadata.char_count,
            "chunk_count": self.metadata.chunk_count,
            "markdown": self.markdown,
            "chunks": [
                {
                    "id": c.id,
                    "text": c.text,
                    "metadata": c.metadata,
                    "embedding": c.embedding,
                }
                for c in self.chunks
            ],
        }
