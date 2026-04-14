"""Unified LLM service supporting Claude and OpenAI."""

from __future__ import annotations

from langchain_core.language_models import BaseChatModel

from app.config import settings


def get_llm() -> BaseChatModel:
    """Create an LLM instance based on configuration.

    Returns:
        LangChain chat model configured per settings.

    Raises:
        ValueError: If the LLM provider is not supported.
    """
    if settings.llm_provider == "claude":
        from langchain_anthropic import ChatAnthropic

        return ChatAnthropic(
            model=settings.llm_model,
            anthropic_api_key=settings.anthropic_api_key,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )
    elif settings.llm_provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm_model,
            openai_api_key=settings.openai_api_key,
            temperature=settings.llm_temperature,
            max_tokens=settings.llm_max_tokens,
        )
    else:
        raise ValueError(f"Unsupported LLM provider: {settings.llm_provider}")
