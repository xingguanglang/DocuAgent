"""Pydantic request/response models."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, EmailStr, Field

# --- Auth ---


class RegisterRequest(BaseModel):
    """User registration request."""

    email: EmailStr
    password: str = Field(..., min_length=8)
    name: str = Field(..., min_length=1, max_length=100)


class LoginRequest(BaseModel):
    """User login request."""

    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    """Login response with JWT token."""

    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    """Public user information."""

    id: str
    email: str
    name: str
    created_at: datetime


# --- Chat ---


class ChatRequest(BaseModel):
    """Chat message request."""

    message: str = Field(..., min_length=1, max_length=10000)
    conversation_id: str | None = None


class ChatMessage(BaseModel):
    """Single chat message."""

    id: str
    role: str  # "user" | "assistant"
    content: str
    sources: list[Source] = []
    tool_calls: list[ToolCallInfo] = []
    created_at: datetime


class Source(BaseModel):
    """Citation source from RAG retrieval."""

    document_id: str
    document_name: str
    chunk_text: str
    relevance_score: float
    page_number: int | None = None
    

class ToolCallInfo(BaseModel):
    """Agent tool call metadata."""

    tool_name: str
    input_summary: str
    output_summary: str


class ChatHistoryResponse(BaseModel):
    """Chat history response."""

    conversation_id: str
    messages: list[ChatMessage]


# --- Documents ---


class DocumentResponse(BaseModel):
    """Document metadata."""

    id: str
    filename: str
    file_type: str
    size_bytes: int
    chunk_count: int
    status: str  # "processing" | "ready" | "error"
    uploaded_at: datetime


class DocumentListResponse(BaseModel):
    """List of documents."""

    documents: list[DocumentResponse]
    total: int
