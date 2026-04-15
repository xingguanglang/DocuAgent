"""Tests for chat endpoints."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_chat_requires_auth(client: AsyncClient) -> None:
    """Chat endpoint requires authentication."""
    response = await client.post(
        "/api/v1/chat/",
        json={"message": "Hello"},
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_chat_streams_sse_response(auth_client: AsyncClient) -> None:
    """Chat endpoint returns SSE stream with agent events."""

    async def mock_run(query, conversation_history=None):
        yield {"type": "thought", "content": "Thinking about the question..."}
        yield {"type": "answer", "content": "This is a test answer."}

    mock_engine = AsyncMock()
    mock_engine.run = mock_run

    with patch("app.api.routes.chat.AgentEngine") as mock_cls:
        mock_cls.return_value = mock_engine
        response = await auth_client.post(
            "/api/v1/chat/",
            json={"message": "What is Python?"},
        )

    assert response.status_code == 200
    assert "text/event-stream" in response.headers.get("content-type", "")

    # Check that the response body contains SSE events
    body = response.text
    assert "event: conversation_id" in body
    assert "event: thought" in body
    assert "event: message" in body
    assert "event: done" in body


@pytest.mark.asyncio
async def test_chat_handles_agent_error(auth_client: AsyncClient) -> None:
    """Chat endpoint handles agent errors gracefully."""

    async def mock_run_error(query, conversation_history=None):
        raise RuntimeError("LLM API is down")
        yield

    mock_engine = AsyncMock()
    mock_engine.run = mock_run_error

    with patch("app.api.routes.chat.AgentEngine") as mock_cls:
        mock_cls.return_value = mock_engine
        response = await auth_client.post(
            "/api/v1/chat/",
            json={"message": "Hello"},
        )

    assert response.status_code == 200
    body = response.text
    assert "event: message" in body
    assert "error" in body.lower() or "sorry" in body.lower()


@pytest.mark.asyncio
async def test_list_conversations_empty(auth_client: AsyncClient) -> None:
    """Listing conversations for new user returns empty list."""
    response = await auth_client.get("/api/v1/chat/conversations")
    assert response.status_code == 200
    data = response.json()
    assert data["conversations"] == []
    assert data["total"] == 0


@pytest.mark.asyncio
async def test_list_conversations_requires_auth(client: AsyncClient) -> None:
    """Listing conversations without auth returns 401."""
    response = await client.get("/api/v1/chat/conversations")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_conversation_history_after_chat(auth_client: AsyncClient) -> None:
    """After a chat, the conversation appears in the list and messages are accessible."""

    async def mock_run(query, conversation_history=None):
        yield {"type": "answer", "content": "Hello back!"}

    mock_engine = AsyncMock()
    mock_engine.run = mock_run

    with patch("app.api.routes.chat.AgentEngine") as mock_cls:
        mock_cls.return_value = mock_engine
        await auth_client.post(
            "/api/v1/chat/",
            json={"message": "Hello there"},
        )

    # Conversation should now exist
    response = await auth_client.get("/api/v1/chat/conversations")
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    conv_id = data["conversations"][0]["id"]

    # Fetch messages for this conversation
    msg_response = await auth_client.get(f"/api/v1/chat/conversations/{conv_id}")
    assert msg_response.status_code == 200
    msg_data = msg_response.json()
    assert len(msg_data["messages"]) >= 2  # user + assistant


@pytest.mark.asyncio
async def test_delete_conversation(auth_client: AsyncClient) -> None:
    """Deleting a conversation removes it and its messages."""

    async def mock_run(query, conversation_history=None):
        yield {"type": "answer", "content": "Reply"}

    mock_engine = AsyncMock()
    mock_engine.run = mock_run

    with patch("app.api.routes.chat.AgentEngine") as mock_cls:
        mock_cls.return_value = mock_engine
        await auth_client.post(
            "/api/v1/chat/",
            json={"message": "Test message"},
        )

    # Get conversation id
    list_res = await auth_client.get("/api/v1/chat/conversations")
    conv_id = list_res.json()["conversations"][0]["id"]

    # Delete it
    del_res = await auth_client.delete(f"/api/v1/chat/conversations/{conv_id}")
    assert del_res.status_code == 200

    # Verify it's gone
    list_res2 = await auth_client.get("/api/v1/chat/conversations")
    ids = [c["id"] for c in list_res2.json()["conversations"]]
    assert conv_id not in ids


@pytest.mark.asyncio
async def test_get_nonexistent_conversation(auth_client: AsyncClient) -> None:
    """Getting a non-existent conversation returns 404."""
    response = await auth_client.get("/api/v1/chat/conversations/nonexistent-id")
    assert response.status_code == 404
