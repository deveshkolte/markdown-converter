"""Embedding model wrapper.

Uses ChromaDB's default ONNX-powered embedding function
(``all-MiniLM-L6-v2``) so no GPU or PyTorch is required.

Why *all-MiniLM-L6-v2*?
    - **384 dimensions** — compact enough for fast search, rich enough for
      semantic understanding.
    - **ONNX runtime** — runs on CPU with minimal dependencies.
    - **Free and local** — no API keys, no data leaving your machine.
    - **Strong benchmarks** — scores 58.80 on MTEB, competitive with much
      larger models.

Alternatives considered:
    ========================= ======== =========== ===========================
    Model                     Dims     MTEB Score  Notes
    ========================= ======== =========== ===========================
    all-MiniLM-L6-v2          384      58.80       **Chosen** — best perf/size
    BAAI/bge-small-en-v1.5    384      57.81       Slightly lower recall
    text-embedding-3-small    1536     62.30       OpenAI — paid, 3 KB/docs
    instructor-xl             768      64.70       Great but needs GPU
    ========================= ======== =========== ===========================
"""

from __future__ import annotations

from typing import Any

from .logger import get_logger

logger = get_logger()

_embedding_function: Any = None


def _get_embedding_function() -> Any:
    """Lazy-init the embedding function (ChromaDB default)."""
    global _embedding_function
    if _embedding_function is not None:
        return _embedding_function

    try:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        _embedding_function = ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])
        logger.debug("Initialised ONNXMiniLM_L6_V2 embedding function")
    except ImportError:
        logger.warning("chromadb not installed. Install with: pip install markdown-converter[rag]")
        _embedding_function = None

    return _embedding_function


def embed_text(text: str) -> list[float]:
    """Embed a single text string.

    Args:
        text: The input text.

    Returns:
        A 384-dimensional embedding vector.
    """
    fn = _get_embedding_function()
    if fn is None:
        logger.error("Embedding function unavailable")
        return []
    return fn([text])[0]  # type: ignore[index]


def embed_texts(texts: list[str]) -> list[list[float]]:
    """Embed a batch of texts (more efficient than calling one-by-one).

    Args:
        texts: List of text strings to embed.

    Returns:
        A list of embedding vectors.
    """
    fn = _get_embedding_function()
    if fn is None:
        logger.error("Embedding function unavailable")
        return []
    return fn(texts)  # type: ignore[return-value]
