"""Hybrid retriever combining vector similarity and BM25 keyword search."""

from __future__ import annotations

from langchain_core.documents import Document
from rank_bm25 import BM25Okapi

from app.services.vector_store import VectorStoreService


class HybridRetriever:
    """Combines vector similarity search with BM25 keyword search.

    Uses reciprocal rank fusion (RRF) to merge results from both
    retrieval methods.
    """

    def __init__(self) -> None:
        """Initialize the hybrid retriever."""
        self._vector_store = VectorStoreService()

    async def retrieve(
        self,
        query: str,
        top_k: int = 5,
        vector_weight: float = 0.7,
    ) -> list[Document]:
        """Retrieve relevant documents using hybrid search.

        First does vector similarity search via ChromaDB, then applies BM25
        reranking on the results for keyword relevance, and fuses both
        rankings via reciprocal rank fusion.

        Args:
            query: The search query.
            top_k: Number of documents to return.
            vector_weight: Weight for vector results (BM25 gets 1 - weight).

        Returns:
            List of documents ranked by combined relevance.
        """
        # Step 1: vector search, fetch more candidates
        candidates = await self._vector_store.similarity_search(
            query, top_k=top_k * 3
        )

        if not candidates:
            return []

        # Step 2: BM25 keyword scoring
        tokenized_corpus = [doc.page_content.lower().split() for doc in candidates]
        bm25 = BM25Okapi(tokenized_corpus)
        bm25_scores = bm25.get_scores(query.lower().split())

        # Step 3: reciprocal rank fusion (RRF)
        # Vector rank: candidates are sorted by similarity, index = rank
        k = 60  # RRF constant
        fused_scores: list[tuple[int, float]] = []

        for i, _doc in enumerate(candidates):
            vector_rank = i + 1
            # BM25 rank: sorted by score descending
            bm25_rank = sorted(
                range(len(bm25_scores)),
                key=lambda x: bm25_scores[x],
                reverse=True,
            ).index(i) + 1

            rrf_score = (
                vector_weight * (1.0 / (k + vector_rank))
                + (1 - vector_weight) * (1.0 / (k + bm25_rank))
            )
            fused_scores.append((i, rrf_score))

        # Sort by fused score descending, take top_k
        fused_scores.sort(key=lambda x: x[1], reverse=True)

        return [candidates[i] for i, _ in fused_scores[:top_k]]
