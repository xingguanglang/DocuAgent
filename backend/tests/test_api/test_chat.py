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
