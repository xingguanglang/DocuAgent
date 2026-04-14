"""RAG retrieval tool for the agent."""

from __future__ import annotations

from typing import Any


async def rag_search(query: str, top_k: int = 5) -> dict[str, Any]:
    """Search uploaded documents using RAG retrieval.

    Args:
        query: Search query.
        top_k: Number of results to return.

    Returns:
        Dict with retrieved chunks and metadata.
    """
    # TODO: Integrate with retriever and reranker
    raise NotImplementedError
