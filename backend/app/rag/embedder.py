"""Embedding generation for document chunks."""

from __future__ import annotations

from langchain_core.embeddings import Embeddings

from app.config import settings


def get_embedding_model() -> Embeddings:
    """Create an embedding model based on configuration.

    Returns:
        LangChain Embeddings instance configured per settings.

    Raises:
        ValueError: If the embedding provider is not supported.
    """
    if settings.embedding_provider == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=settings.embedding_model,
            openai_api_key=settings.openai_api_key,
        )
    elif settings.embedding_provider == "local":
        from langchain_community.embeddings import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(model_name=settings.embedding_model)
    else:
        raise ValueError(f"Unsupported embedding provider: {settings.embedding_provider}")
