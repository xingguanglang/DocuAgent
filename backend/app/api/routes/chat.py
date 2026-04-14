"""Chat endpoints with SSE streaming."""

from __future__ import annotations

import json
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sse_starlette.sse import EventSourceResponse

from app.api.dependencies import get_current_user
from app.models.schemas import ChatRequest

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

    async def event_generator() -> Any:
        """Generate SSE events for the chat response."""
        yield {"event": "thought", "data": "Analyzing your question..."}

        yield {"event": "action", "data": json.dumps({"tool": "rag_search", "query": request.message})}

        yield {
            "event": "message",
            "data": (
                f"Thanks for your question: \"{request.message}\"\n\n"
                "I'm the DocuAgent assistant. The full RAG + Agent pipeline is coming soon. "
                "Once implemented, I'll be able to:\n"
                "- Search your uploaded documents for relevant information\n"
                "- Execute code to analyze data\n"
                "- Query databases for structured information\n"
                "- Search the web for additional context\n\n"
                "For now, try uploading a document and checking the /health endpoint!"
            ),
        }

        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())
