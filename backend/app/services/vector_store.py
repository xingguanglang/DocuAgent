"""ChromaDB vector store service."""

from __future__ import annotations

import uuid
from typing import Any

import chromadb
from langchain_core.documents import Document

from app.config import settings
from app.rag.embedder import get_embedding_model


class VectorStoreService:
    """Manages ChromaDB collections for document embeddings."""

    def __init__(self) -> None:
        """Initialize ChromaDB client."""
        self._client = chromadb.HttpClient(
            host=settings.chroma_host,
            port=settings.chroma_port,
        )
        self._embedding_model = get_embedding_model()

    def get_or_create_collection(self, name: str = "documents") -> Any:
        """Get or create a ChromaDB collection.

        Args:
            name: Collection name.

        Returns:
            ChromaDB collection instance.
        """
        return self._client.get_or_create_collection(name=name)

    async def add_documents(
        self,
        documents: list[Document],
        collection_name: str = "documents",
    ) -> list[str]:
        """Embed and store documents in ChromaDB.

        Args:
            documents: LangChain Document objects to store.
            collection_name: Target collection name.

        Returns:
            List of document IDs assigned by ChromaDB.
        """
        collection = self.get_or_create_collection(collection_name)

        texts = [doc.page_content for doc in documents]
        metadatas = [doc.metadata for doc in documents]
        ids = [str(uuid.uuid4()) for _ in documents]

        embeddings = self._embedding_model.embed_documents(texts)

        collection.add(
            ids=ids,
            embeddings=embeddings,
            documents=texts,
            metadatas=metadatas,
        )

        return ids

    async def similarity_search(
        self,
        query: str,
        top_k: int = 10,
        collection_name: str = "documents",
    ) -> list[Document]:
        """Search for similar documents by query.

        Args:
            query: Search query text.
            top_k: Number of results to return.
            collection_name: Collection to search in.

        Returns:
            List of relevant documents with scores.
        """
        collection = self.get_or_create_collection(collection_name)

        query_embedding = self._embedding_model.embed_query(query)

        results = collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            include=["documents", "metadatas", "distances"],
        )

        documents = []
        for text, metadata in zip(
            results["documents"][0],
            results["metadatas"][0],
        ):
            documents.append(Document(page_content=text, metadata=metadata))

        return documents
