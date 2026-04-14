"""Document upload and management endpoints."""

from __future__ import annotations

import os
import uuid
from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, UploadFile, status
from sqlalchemy import select

from app.api.dependencies import get_current_user
from app.config import settings
from app.models.database import Document, async_session
from app.models.schemas import DocumentListResponse, DocumentResponse
from app.rag.chunker import chunk_documents
from app.rag.loader import load_document

router = APIRouter()

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt"}


@router.post("/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile,
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> DocumentResponse:
    """Upload a document for processing.

    Accepts PDF, Markdown, and plain text files. The document is chunked
    and stored. Vector embedding will be added when the RAG pipeline is connected.

    Args:
        file: Uploaded file (PDF, MD, or TXT).
        user: Authenticated user from JWT token.

    Returns:
        Document metadata including processing status.
    """
    filename = file.filename or "untitled"
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type {ext} not supported. Allowed: {ALLOWED_EXTENSIONS}",
        )

    content = await file.read()
    size_bytes = len(content)

    if size_bytes > settings.max_upload_size_mb * 1024 * 1024:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File too large. Max size: {settings.max_upload_size_mb}MB",
        )

    doc_id = str(uuid.uuid4())
    file_path = os.path.join(settings.upload_dir, f"{doc_id}{ext}")
    os.makedirs(settings.upload_dir, exist_ok=True)

    with open(file_path, "wb") as f:
        f.write(content)

    try:
        docs = await load_document(file_path)
        chunks = chunk_documents(docs)
        chunk_count = len(chunks)
        doc_status = "ready"
    except Exception:
        chunk_count = 0
        doc_status = "error"

    async with async_session() as session:
        document = Document(
            id=doc_id,
            user_id=user["user_id"],
            filename=filename,
            file_type=ext.lstrip("."),
            size_bytes=size_bytes,
            chunk_count=chunk_count,
            status=doc_status,
        )
        session.add(document)
        await session.commit()
        await session.refresh(document)

        return DocumentResponse(
            id=document.id,
            filename=document.filename,
            file_type=document.file_type,
            size_bytes=document.size_bytes,
            chunk_count=document.chunk_count,
            status=document.status,
            uploaded_at=document.uploaded_at,
        )


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
    async with async_session() as session:
        result = await session.execute(
            select(Document).where(Document.user_id == user["user_id"])
        )
        documents = result.scalars().all()

        return DocumentListResponse(
            documents=[
                DocumentResponse(
                    id=doc.id,
                    filename=doc.filename,
                    file_type=doc.file_type,
                    size_bytes=doc.size_bytes,
                    chunk_count=doc.chunk_count,
                    status=doc.status,
                    uploaded_at=doc.uploaded_at,
                )
                for doc in documents
            ],
            total=len(documents),
        )


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
    async with async_session() as session:
        result = await session.execute(
            select(Document).where(
                Document.id == document_id,
                Document.user_id == user["user_id"],
            )
        )
        document = result.scalar_one_or_none()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found",
            )

        file_path = os.path.join(
            settings.upload_dir, f"{document.id}.{document.file_type}"
        )
        if os.path.exists(file_path):
            os.remove(file_path)

        await session.delete(document)
        await session.commit()

        return {"message": "Document deleted successfully"}
