"""Tests for the web search tool."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.agent.tools.web_search import web_search


@pytest.mark.asyncio
async def test_web_search_returns_results():
    """Web search returns formatted results from DuckDuckGo."""
    mock_results = [
        {"title": "Python.org", "url": "https://python.org", "snippet": "Official Python site."},
        {"title": "Python Tutorial", "url": "https://docs.python.org", "snippet": "Learn Python."},
    ]

    with patch(
        "app.agent.tools.web_search._search_sync",
        return_value=mock_results,
    ):
        result = await web_search("Python programming", num_results=2)

    assert result["query"] == "Python programming"
    assert result["num_results"] == 2
    assert len(result["results"]) == 2
    assert result["results"][0]["title"] == "Python.org"
    assert result["results"][0]["url"] == "https://python.org"
    assert result["results"][0]["snippet"] == "Official Python site."


@pytest.mark.asyncio
async def test_web_search_handles_error():
    """Web search handles exceptions gracefully."""
    with patch(
        "app.agent.tools.web_search._search_sync",
        side_effect=RuntimeError("Network error"),
    ):
        result = await web_search("failing query")

    assert result["num_results"] == 0
    assert result["results"] == []
    assert "error" in result


@pytest.mark.asyncio
async def test_web_search_caps_num_results():
    """Web search caps num_results at 10."""
    with patch(
        "app.agent.tools.web_search._search_sync",
        return_value=[],
    ) as mock_search:
        await web_search("test", num_results=50)

    # Verify _search_sync was called with capped num_results=10
    mock_search.assert_called_once_with("test", 10)


@pytest.mark.asyncio
async def test_web_search_empty_results():
    """Web search returns empty when no results found."""
    with patch(
        "app.agent.tools.web_search._search_sync",
        return_value=[],
    ):
        result = await web_search("extremely obscure query xyz123")

    assert result["num_results"] == 0
    assert result["results"] == []
    assert "error" not in result
