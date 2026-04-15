"""Web search tool for the agent."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

logger = logging.getLogger(__name__)


async def web_search(query: str, num_results: int = 5) -> dict[str, Any]:
    """Search the web using DuckDuckGo and return results.

    Uses the duckduckgo-search library which requires no API key.
    The search runs in a thread pool to avoid blocking the event loop
    since the library is synchronous.

    Args:
        query: Search query string.
        num_results: Number of results to return (max 10).

    Returns:
        Dict with query, result count, and list of search results.
    """
    num_results = min(num_results, 10)

    try:
        results = await asyncio.to_thread(_search_sync, query, num_results)
    except Exception as e:
        logger.exception("Web search failed for query: %s", query)
        return {
            "query": query,
            "num_results": 0,
            "results": [],
            "error": f"Search failed: {e!s}",
        }

    return {
        "query": query,
        "num_results": len(results),
        "results": results,
    }


def _search_sync(query: str, num_results: int) -> list[dict[str, str]]:
    """Run DuckDuckGo search synchronously.

    Args:
        query: Search query.
        num_results: Max number of results.

    Returns:
        List of result dicts with title, url, and snippet.
    """
    from duckduckgo_search import DDGS

    results: list[dict[str, str]] = []

    with DDGS() as ddgs:
        for r in ddgs.text(query, max_results=num_results):
            results.append(
                {
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                }
            )

    return results
