"""Tests for document endpoints."""

from __future__ import annotations

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_list_documents_empty(auth_client: AsyncClient) -> None:
    """Listing documents for new user returns empty list."""
    response = await auth_client.get("/api/v1/documents/")
    assert response.status_code == 200
    data = response.json()
    assert data["documents"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_documents_requires_auth(client: AsyncClient) -> None:
    """Listing documents without auth returns 401."""
    response = await client.get("/api/v1/documents/")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_upload_txt_document(auth_client: AsyncClient) -> None:
    """Uploading a .txt file succeeds and returns document metadata."""
    response = await auth_client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.txt", b"Hello, this is a test document.", "text/plain")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["filename"] == "test.txt"
    assert data["file_type"] == "txt"
    assert data["status"] == "ready"
    assert data["chunk_count"] >= 1


@pytest.mark.asyncio
async def test_upload_unsupported_file(auth_client: AsyncClient) -> None:
    """Uploading an unsupported file type returns 400."""
    response = await auth_client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.exe", b"binary content", "application/octet-stream")},
    )
    assert response.status_code == 400
