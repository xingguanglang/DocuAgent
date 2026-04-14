"""Web search tool for the agent."""

from __future__ import annotations

from typing import Any


async def web_search(query: str, num_results: int = 5) -> list[dict[str, Any]]:
    """Search the web for information.

    Args:
        query: Search query string.
        num_results: Number of results to return.

    Returns:
        List of search results with title, url, and snippet.
    """
    # TODO: Implement web search (e.g., via SerpAPI or Tavily)
    raise NotImplementedError
