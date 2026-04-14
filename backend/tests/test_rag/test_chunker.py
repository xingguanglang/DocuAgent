"""Tests for text chunking."""

from __future__ import annotations

from langchain_core.documents import Document

from app.rag.chunker import chunk_documents


def test_chunk_documents_splits_long_text() -> None:
    """Chunker splits a long document into multiple chunks."""
    long_text = "This is a sentence. " * 200  # ~4000 chars
    docs = [Document(page_content=long_text, metadata={"source": "test.txt"})]
    chunks = chunk_documents(docs, chunk_size=500, chunk_overlap=50)
    assert len(chunks) > 1
    for chunk in chunks:
        assert len(chunk.page_content) <= 500 + 50  # allow some flexibility
        assert chunk.metadata["source"] == "test.txt"


def test_chunk_documents_preserves_short_text() -> None:
    """Chunker does not split text shorter than chunk_size."""
    short_text = "Short document content."
    docs = [Document(page_content=short_text, metadata={"source": "test.txt"})]
    chunks = chunk_documents(docs, chunk_size=1000, chunk_overlap=100)
    assert len(chunks) == 1
    assert chunks[0].page_content == short_text
