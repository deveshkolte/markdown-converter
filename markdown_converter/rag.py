"""RAG pipeline orchestrator.

Ties together document ingestion, embedding, vector search, and LLM querying
into a single ``ask_document()`` function.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from . import vectordb
from .logger import get_logger
from .pipeline import run_pipeline

logger = get_logger()


def ingest_document(
    input_path: str | Path,
    collection_name: str = "documents",
    chunk_strategy: str = "recursive",
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
) -> dict[str, Any]:
    """Ingest a document into the vector store for RAG queries.

    Runs the full pipeline (convert → chunk → embed → store).

    Args:
        input_path: Path to the source document.
        collection_name: ChromaDB collection name.
        chunk_strategy, chunk_size, chunk_overlap: Chunking parameters.

    Returns:
        A summary dict with ``"document"``, ``"chunks_added"``, and
        ``"total_chunks"``.
    """
    doc = run_pipeline(
        input_path,
        chunk_strategy=chunk_strategy,
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
    )

    chunk_dicts = [{"id": c.id, "text": c.text, "metadata": c.metadata} for c in doc.chunks]

    doc_id = doc.metadata.title
    added = vectordb.add_document(doc_id, chunk_dicts, collection_name=collection_name)
    total = vectordb.count(collection_name=collection_name)

    logger.info(
        "Ingested '%s': %d chunks added (total in DB: %d)",
        doc_id,
        added,
        total,
    )

    return {
        "document": doc_id,
        "chunks_added": added,
        "total_chunks": total,
    }


def ask_document(
    question: str,
    document_path: str | Path | None = None,
    collection_name: str = "documents",
    n_results: int = 5,
    model: str = "openai/gpt-4o-mini",
) -> dict[str, Any]:
    """Ask a question about ingested documents.

    If *document_path* is provided, restricts the search to chunks from
    that document.

    Args:
        question: Natural language question.
        document_path: Optional — restrict search to this document.
        collection_name: ChromaDB collection to search.
        n_results: Number of context chunks to retrieve.
        model: OpenRouter model identifier.

    Returns:
        A dict with ``"question"``, ``"answer"``, ``"sources"`` (list of
        chunk texts), and ``"model"``.
    """
    where = None
    if document_path is not None:
        doc_id = Path(document_path).stem
        where = {"doc_id": doc_id}

    results = vectordb.query(
        question,
        n_results=n_results,
        collection_name=collection_name,
        where=where,
    )

    if not results:
        return {
            "question": question,
            "answer": "No relevant chunks found. Ingest a document first.",
            "sources": [],
            "model": model,
        }

    from .llm import ask_with_context

    answer = ask_with_context(question, results, model=model)

    return {
        "question": question,
        "answer": answer,
        "sources": [r["text"] for r in results],
        "model": model,
    }
