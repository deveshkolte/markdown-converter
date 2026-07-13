"""OpenRouter LLM client for querying documents.

Uses OpenRouter's unified API to access 200+ models (GPT-4, Claude, Gemini,
Llama, etc.) with a single API key.

Environment variable: ``OPENROUTER_API_KEY``
"""

from __future__ import annotations

import os
from typing import Any

from .logger import get_logger

logger = get_logger()

_http_client: Any = None
DEFAULT_MODEL = "openai/gpt-4o-mini"


def _get_client() -> Any:
    """Lazy-init the HTTPX client."""
    global _http_client
    if _http_client is not None:
        return _http_client

    import httpx

    api_key = os.environ.get("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError(
            "OPENROUTER_API_KEY environment variable is not set. "
            "Get a key at https://openrouter.ai/keys"
        )

    _http_client = httpx.Client(
        base_url="https://openrouter.ai/api/v1",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/deveshkolte/markdown-converter",
            "X-Title": "Markdown Converter RAG",
        },
        timeout=60.0,
    )
    logger.debug("OpenRouter client initialised (model: %s)", DEFAULT_MODEL)
    return _http_client


def ask(
    system_prompt: str,
    user_prompt: str,
    model: str = DEFAULT_MODEL,
    temperature: float = 0.3,
    max_tokens: int = 2048,
) -> str:
    """Send a chat completion request to OpenRouter.

    Args:
        system_prompt: The system-level instruction.
        user_prompt: The user's question or input.
        model: Model identifier (default: ``"openai/gpt-4o-mini"``).
        temperature: Sampling temperature (0.0 = deterministic).
        max_tokens: Maximum tokens in the response.

    Returns:
        The model's text response.
    """
    client = _get_client()

    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": temperature,
        "max_tokens": max_tokens,
    }

    logger.debug("LLM request: model=%s, system=%d chars, user=%d chars",
                  model, len(system_prompt), len(user_prompt))

    try:
        response = client.post("/chat/completions", json=payload)
        response.raise_for_status()
        data = response.json()
        content = data["choices"][0]["message"]["content"]
        logger.debug("LLM response: %d chars", len(content))
        return content
    except Exception as exc:
        logger.exception("OpenRouter API call failed: %s", exc)
        return f"[Error: {exc}]"


def ask_with_context(
    question: str,
    context_chunks: list[dict[str, Any]],
    model: str = DEFAULT_MODEL,
) -> str:
    """Ask a question with retrieved document chunks as context.

    Args:
        question: The user's question.
        context_chunks: List of relevant chunks from the vector store.
        model: Model identifier.

    Returns:
        The model's answer with citations.
    """
    context_text = "\n\n---\n\n".join(
        f"[Chunk {i+1}] {c['text']}"
        for i, c in enumerate(context_chunks)
    )

    system_prompt = (
        "You are a precise document analysis assistant. "
        "Answer the user's question based *only* on the provided document chunks. "
        "If the chunks don't contain enough information, say so. "
        "Cite the specific chunk numbers you used.\n\n"
        "Return your answer in this format:\n"
        "**Answer**: <your answer>\n"
        "**Sources**: Chunk 1, Chunk 3, ..."
    )

    user_prompt = f"Context:\n{context_text}\n\nQuestion: {question}"

    return ask(system_prompt, user_prompt, model=model)
