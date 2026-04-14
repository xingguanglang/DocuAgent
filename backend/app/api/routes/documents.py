"""Document upload and management endpoints."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, UploadFile

from app.api.dependencies import get_current_user
from app.models.schemas import DocumentListResponse, DocumentResponse

router = APIRouter()


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile,
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> DocumentResponse:
    """Upload a document for processing.

    Accepts PDF, Markdown, and plain text files. The document is chunked,
    embedded, and stored in the vector database.

    Args:
        file: Uploaded file (PDF, MD, or TXT).
        user: Authenticated user from JWT token.

    Returns:
        Document metadata including processing status.
    """
    # TODO: Implement document upload + RAG pipeline ingestion
    raise NotImplementedError


@router.get("/", response_model=DocumentListResponse)
async def list_documents(
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> DocumentListResponse:
    """List all documents uploaded by the current user.

    Args:
        user: Authenticated user from JWT token.

    Returns:
        List of document metadata.
    """
    # TODO: Implement document listing
    raise NotImplementedError


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a document and its vector embeddings.

    Args:
        document_id: UUID of the document to delete.
        user: Authenticated user from JWT token.

    Returns:
        Confirmation message.
    """
    # TODO: Implement document deletion
    raise NotImplementedError
