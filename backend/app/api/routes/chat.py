"""Chat endpoints with SSE streaming."""

from __future__ import annotations

import logging
import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Depends
from sqlalchemy import select
from sse_starlette.sse import EventSourceResponse

from app.agent.engine import AgentEngine
from app.agent.memory import ConversationMemory
from app.api.dependencies import get_current_user
from app.models.database import Conversation, Message, async_session
from app.models.schemas import (
    ChatHistoryResponse,
    ChatMessage,
    ChatRequest,
    ConversationListResponse,
    ConversationResponse,
)

logger = logging.getLogger(__name__)

router = APIRouter()

# In-memory conversation memories (per conversation_id)
_memories: dict[str, ConversationMemory] = {}


def _get_memory(conversation_id: str) -> ConversationMemory:
    """Get or create a ConversationMemory for a conversation.

    Args:
        conversation_id: The conversation identifier.

    Returns:
        ConversationMemory instance.
    """
    if conversation_id not in _memories:
        _memories[conversation_id] = ConversationMemory()
    return _memories[conversation_id]


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
    conversation_id = request.conversation_id or str(uuid.uuid4())
    user_id = user["user_id"]

    # Load conversation memory
    memory = _get_memory(conversation_id)
    memory.add_message("user", request.message)

    async def event_generator() -> Any:
        """Generate SSE events from the agent's ReAct loop."""
        # Send conversation ID first so frontend can track it
        yield {
            "event": "conversation_id",
            "data": conversation_id,
        }

        full_answer = ""

        try:
            engine = AgentEngine()

            async for event in engine.run(
                query=request.message,
                conversation_history=memory.get_messages()[:-1],  # exclude current
            ):
                event_type = event["type"]
                content = event["content"]

                if event_type == "thought":
                    yield {"event": "thought", "data": content}

                elif event_type == "action":
                    yield {"event": "action", "data": content}

                elif event_type == "observation":
                    yield {"event": "observation", "data": content}

                elif event_type == "answer":
                    full_answer = content
                    yield {"event": "message", "data": content}

        except Exception:
            logger.exception("Agent error for conversation %s", conversation_id)
            full_answer = (
                "Sorry, I encountered an error while processing your request. "
                "Please try again."
            )
            yield {"event": "message", "data": full_answer}

        # Save assistant response to memory
        if full_answer:
            memory.add_message("assistant", full_answer)

        # Persist messages to database
        try:
            await _persist_messages(
                conversation_id=conversation_id,
                user_id=user_id,
                user_message=request.message,
                assistant_message=full_answer,
            )
        except Exception:
            logger.exception("Failed to persist messages for %s", conversation_id)

        yield {"event": "done", "data": ""}

    return EventSourceResponse(event_generator())


async def _persist_messages(
    conversation_id: str,
    user_id: str,
    user_message: str,
    assistant_message: str,
) -> None:
    """Save conversation messages to the database.

    Args:
        conversation_id: The conversation identifier.
        user_id: The user's ID.
        user_message: The user's message text.
        assistant_message: The assistant's response text.
    """
    async with async_session() as session:
        # Get or create conversation
        result = await session.execute(
            select(Conversation).where(Conversation.id == conversation_id)
        )
        conversation = result.scalar_one_or_none()

        if conversation is None:
            # Create a new conversation with a title from the first message
            title = user_message[:80] + ("..." if len(user_message) > 80 else "")
            conversation = Conversation(
                id=conversation_id,
                user_id=user_id,
                title=title,
            )
            session.add(conversation)
            await session.flush()

        # Add user message
        session.add(
            Message(
                conversation_id=conversation_id,
                role="user",
                content=user_message,
            )
        )

        # Add assistant message
        if assistant_message:
            session.add(
                Message(
                    conversation_id=conversation_id,
                    role="assistant",
                    content=assistant_message,
                )
            )

        await session.commit()


@router.get("/conversations", response_model=ConversationListResponse)
async def list_conversations(
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> ConversationListResponse:
    """List all conversations for the current user.

    Returns conversations ordered by most recent first.

    Args:
        user: Authenticated user from JWT token.

    Returns:
        List of conversation summaries.
    """
    async with async_session() as session:
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == user["user_id"])
            .order_by(Conversation.created_at.desc())
        )
        conversations = result.scalars().all()

        return ConversationListResponse(
            conversations=[
                ConversationResponse(
                    id=conv.id,
                    title=conv.title,
                    created_at=conv.created_at,
                )
                for conv in conversations
            ],
            total=len(conversations),
        )


@router.get("/conversations/{conversation_id}", response_model=ChatHistoryResponse)
async def get_conversation_messages(
    conversation_id: str,
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> ChatHistoryResponse:
    """Get all messages for a specific conversation.

    Args:
        conversation_id: UUID of the conversation.
        user: Authenticated user from JWT token.

    Returns:
        Conversation messages ordered chronologically.
    """
    from fastapi import HTTPException, status

    async with async_session() as session:
        # Verify the conversation belongs to this user
        conv_result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user["user_id"],
            )
        )
        if not conv_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        result = await session.execute(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        )
        messages = result.scalars().all()

        return ChatHistoryResponse(
            conversation_id=conversation_id,
            messages=[
                ChatMessage(
                    id=msg.id,
                    role=msg.role,
                    content=msg.content,
                    sources=[],
                    tool_calls=[],
                    created_at=msg.created_at,
                )
                for msg in messages
            ],
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user: Annotated[dict[str, str], Depends(get_current_user)],
) -> dict[str, str]:
    """Delete a conversation and all its messages.

    Args:
        conversation_id: UUID of the conversation to delete.
        user: Authenticated user from JWT token.

    Returns:
        Confirmation message.
    """
    from fastapi import HTTPException, status

    async with async_session() as session:
        result = await session.execute(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user["user_id"],
            )
        )
        conversation = result.scalar_one_or_none()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found",
            )

        # Delete messages first (foreign key)
        msg_result = await session.execute(
            select(Message).where(Message.conversation_id == conversation_id)
        )
        for msg in msg_result.scalars().all():
            await session.delete(msg)

        await session.delete(conversation)
        await session.commit()

        # Clean up in-memory conversation cache
        _memories.pop(conversation_id, None)

        return {"message": "Conversation deleted successfully"}
