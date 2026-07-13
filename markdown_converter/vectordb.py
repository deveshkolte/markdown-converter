"""Local vector database backed by ChromaDB.

ChromaDB is chosen because:

* **Zero-config** — ``chromadb.Client()`` creates a persistent SQLite-backed
  store immediately.
* **Built-in embedding support** — can use our ONNX MiniLM function directly.
* **Metadata filtering** — attach arbitrary metadata per chunk and filter
  at query time.
* **Local** — no external service, data never leaves your machine.
* **Small footprint** — the database is a directory on disk.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from .logger import get_logger

logger = get_logger()

_client: Any = None
_collection: Any = None


def _get_client(persist_dir: str | None = None) -> Any:
    """Lazy-init the ChromaDB client."""
    global _client
    if _client is not None:
        return _client

    try:
        import chromadb

        persist = persist_dir or os.path.join(
            os.path.dirname(__file__), "..", ".chromadb"
        )
        _client = chromadb.PersistentClient(path=persist)
        logger.debug("ChromaDB client initialised (persist at %s)", persist)
    except ImportError:
        logger.warning(
            "chromadb not installed. Install with: pip install markdown-converter[rag]"
        )
        _client = None

    return _client


def _get_collection(collection_name: str = "documents") -> Any:
    """Get or create a ChromaDB collection."""
    global _collection
    if _collection is not None:
        return _collection

    client = _get_client()
    if client is None:
        return None

    try:
        from chromadb.utils.embedding_functions import ONNXMiniLM_L6_V2

        ef = ONNXMiniLM_L6_V2(preferred_providers=["CPUExecutionProvider"])
        _collection = client.get_or_create_collection(
            name=collection_name,
            embedding_function=ef,
            metadata={"hnsw:space": "cosine"},
        )
        logger.debug("Collection '%s' ready (%d docs)", collection_name, _collection.count())
    except Exception as exc:
        logger.error("Failed to create collection: %s", exc)
        _collection = None

    return _collection


def add_document(
    doc_id: str,
    chunks: list[dict[str, Any]],
    collection_name: str = "documents",
) -> int:
    """Add a document's chunks to the vector store.

    Args:
        doc_id: Unique document identifier (e.g. filename).
        chunks: List of chunk dicts with ``"id"``, ``"text"``, and ``"metadata"``.
        collection_name: ChromaDB collection name.

    Returns:
        Number of chunks added.
    """
    coll = _get_collection(collection_name)
    if coll is None:
        return 0

    ids = [f"{doc_id}__{c['id']}" for c in chunks]
    texts = [c["text"] for c in chunks]
    metadatas = [
        {**c.get("metadata", {}), "doc_id": doc_id, "chunk_id": c["id"]}
        for c in chunks
    ]

    # ChromaDB handles embedding automatically via the collection's embedding function
    coll.add(ids=ids, documents=texts, metadatas=metadatas)
    logger.info("Added %d chunks to collection '%s'", len(chunks), collection_name)
    return len(chunks)


def query(
    query_text: str,
    n_results: int = 5,
    collection_name: str = "documents",
    where: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    """Query the vector store for semantically similar chunks.

    Args:
        query_text: Natural language query.
        n_results: Number of top results to return.
        collection_name: Collection to search.
        where: Optional metadata filter (e.g. ``{"doc_id": "resume.pdf"}``).

    Returns:
        A list of result dicts with ``"id"``, ``"text"``, ``"metadata"``,
        and ``"distance"`` keys.
    """
    coll = _get_collection(collection_name)
    if coll is None:
        return []

    results = coll.query(
        query_texts=[query_text],
        n_results=n_results,
        where=where,
    )

    formatted: list[dict[str, Any]] = []
    if results["ids"] and results["documents"]:
        for i in range(len(results["ids"][0])):
            formatted.append(
                {
                    "id": results["ids"][0][i],
                    "text": results["documents"][0][i],
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                    "distance": results["distances"][0][i] if results["distances"] else 0.0,
                }
            )

    return formatted


def count(collection_name: str = "documents") -> int:
    """Return the number of chunks in the collection."""
    coll = _get_collection(collection_name)
    if coll is None:
        return 0
    return coll.count()


def reset(collection_name: str = "documents") -> None:
    """Delete all chunks in the collection."""
    coll = _get_collection(collection_name)
    if coll is not None:
        coll.delete(where={})
        logger.info("Reset collection '%s'", collection_name)
