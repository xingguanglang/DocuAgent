"""Chat endpoints with SSE streaming."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.api.dependencies import get_current_user
from app.models.schemas import ChatRequest, ChatHistoryResponse

router = APIRouter()


@router.post("/")
async def chat(
    request: ChatRequest,
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> EventSourceResponse:
    """Process a chat message and stream the response via SSE.

    The agent decides which tools to use (RAG, code execution, SQL, web search)
    and streams reasoning steps + final answer.

    Args:
        request: Chat message and conversation context.
        user: Authenticated user from JWT token.

    Returns:
        SSE stream of agent reasoning and response chunks.
    """

    async def event_generator():  # type: ignore[no-untyped-def]
        # TODO: Implement agent-powered chat with SSE streaming
        yield {"event": "message", "data": "Not implemented yet"}
        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())


@router.get("/history", response_model=ChatHistoryResponse)
async def get_chat_history(
    user: Annotated[dict[str, str], Depends(get_current_user)],
    conversation_id: str | None = None,
) -> ChatHistoryResponse:
    """Retrieve chat history for the current user.

    Args:
        user: Authenticated user from JWT token.
        conversation_id: Optional conversation ID to filter by.

    Returns:
        List of chat messages.
    """
    # TODO: Implement chat history retrieval
    raise NotImplementedError
