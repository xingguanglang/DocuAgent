"""RAG retrieval tool for the agent."""

from __future__ import annotations

from typing import Any

from langchain_core.documents import Document

from app.rag.retriever import HybridRetriever

# Module-level retriever instance (reused across calls)
_retriever: HybridRetriever | None = None


def _get_retriever() -> HybridRetriever:
    """Get or create the singleton hybrid retriever.

    Returns:
        HybridRetriever instance.
    """
    global _retriever
    if _retriever is None:
        _retriever = HybridRetriever()
    return _retriever


async def rag_search(query: str, top_k: int = 5) -> dict[str, Any]:
    """Search uploaded documents using RAG hybrid retrieval.

    Performs vector similarity + BM25 keyword search with reciprocal rank
    fusion, then returns the top-k relevant chunks with metadata.

    Args:
        query: Search query.
        top_k: Number of results to return.

    Returns:
        Dict with retrieved chunks and metadata.
    """
    retriever = _get_retriever()
    docs: list[Document] = await retriever.retrieve(query, top_k=top_k)

    results: list[dict[str, Any]] = []
    for i, doc in enumerate(docs):
        results.append(
            {
                "rank": i + 1,
                "content": doc.page_content,
                "document_id": doc.metadata.get("document_id", ""),
                "filename": doc.metadata.get("filename", ""),
                "source": doc.metadata.get("source", ""),
            }
        )

    return {
        "query": query,
        "num_results": len(results),
        "results": results,
    }
