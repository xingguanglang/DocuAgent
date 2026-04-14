"""DocuAgent - AI-powered document assistant."""

from __future__ import annotations

import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import auth, chat, documents
from app.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler for startup/shutdown events."""
    from app.models.database import Base, engine

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    os.makedirs(settings.upload_dir, exist_ok=True)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.app_name,
    version="0.1.0",
    description="AI-powered document assistant with RAG and Agent capabilities",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/v1/auth", tags=["auth"])
app.include_router(chat.router, prefix="/api/v1/chat", tags=["chat"])
app.include_router(documents.router, prefix="/api/v1/documents", tags=["documents"])


@app.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "ok"}
