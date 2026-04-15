"""Tests for the RAG search tool."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from langchain_core.documents import Document

from app.agent.tools.rag_tool import rag_search


@pytest.mark.asyncio
async def test_rag_search_returns_results() -> None:
    """rag_search returns formatted results from the retriever."""
    mock_docs = [
        Document(
            page_content="Python is a programming language.",
            metadata={
                "document_id": "doc-1",
                "filename": "intro.txt",
                "source": "intro.txt",
            },
        ),
        Document(
            page_content="FastAPI is a modern web framework.",
            metadata={
                "document_id": "doc-2",
                "filename": "frameworks.md",
            },
        ),
    ]

    with patch(
        "app.agent.tools.rag_tool._get_retriever"
    ) as mock_get_retriever:
        mock_retriever = AsyncMock()
        mock_retriever.retrieve.return_value = mock_docs
        mock_get_retriever.return_value = mock_retriever

        result = await rag_search("What is Python?", top_k=2)

    assert result["query"] == "What is Python?"
    assert result["num_results"] == 2
    assert len(result["results"]) == 2
    assert result["results"][0]["rank"] == 1
    assert result["results"][0]["content"] == "Python is a programming language."
    assert result["results"][0]["document_id"] == "doc-1"
    assert result["results"][1]["filename"] == "frameworks.md"


@pytest.mark.asyncio
async def test_rag_search_empty_results() -> None:
    """rag_search returns empty results when no documents match."""
    with patch(
        "app.agent.tools.rag_tool._get_retriever"
    ) as mock_get_retriever:
        mock_retriever = AsyncMock()
        mock_retriever.retrieve.return_value = []
        mock_get_retriever.return_value = mock_retriever

        result = await rag_search("nonexistent topic")

    assert result["num_results"] == 0
    assert result["results"] == []
