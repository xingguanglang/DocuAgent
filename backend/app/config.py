"""Application configuration using Pydantic Settings."""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application
    app_name: str = "DocuAgent"
    app_env: str = "development"
    debug: bool = True

    # CORS
    cors_origins: list[str] = ["http://localhost:5173"]

    # LLM
    llm_provider: str = "claude"
    llm_model: str = "claude-sonnet-4-20250514"
    llm_temperature: float = 0.1
    llm_max_tokens: int = 4096
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Embedding
    embedding_provider: str = "openai"
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536

    # PostgreSQL
    database_url: str = (
        "postgresql+asyncpg://docuagent:docuagent@localhost:5432/docuagent"
    )

    # ChromaDB
    chroma_host: str = "localhost"
    chroma_port: int = 8000

    # JWT
    jwt_secret_key: str = "change-me-to-a-random-secret"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440

    # Upload
    upload_dir: str = "/app/uploads"
    max_upload_size_mb: int = 50


settings = Settings()
