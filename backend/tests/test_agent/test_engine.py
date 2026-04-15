"""Tests for the ReAct agent engine."""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.agent.engine import AgentEngine


@pytest.mark.asyncio
async def test_engine_direct_answer() -> None:
    """Agent yields a direct answer when LLM doesn't call any tool."""
    mock_llm = AsyncMock()
    mock_llm.ainvoke.return_value = AsyncMock(
        content="This is a direct answer with no tool calls."
    )

    with patch("app.agent.engine.get_llm", return_value=mock_llm):
        engine = AgentEngine()

    events = []
    async for event in engine.run("Hello"):
        events.append(event)

    assert len(events) == 1
    assert events[0]["type"] == "answer"
    assert "direct answer" in events[0]["content"]


@pytest.mark.asyncio
async def test_engine_rag_tool_call() -> None:
    """Agent calls rag_search tool and then produces final answer."""
    call_count = 0

    async def mock_ainvoke(messages: list) -> AsyncMock:
        nonlocal call_count
        call_count += 1
        result = AsyncMock()
        if call_count == 1:
            # First call: LLM decides to use RAG
            result.content = (
                'Let me search the documents.\n'
                'ACTION: {"tool": "rag_search", "args": {"query": "test query", "top_k": 3}}'
            )
        else:
            # Second call: LLM synthesizes answer from observation
            result.content = "Based on the documents, here is the answer."
        return result

    mock_llm = AsyncMock()
    mock_llm.ainvoke = mock_ainvoke

    mock_rag_result = {
        "query": "test query",
        "num_results": 1,
        "results": [
            {
                "rank": 1,
                "content": "Test chunk content",
                "document_id": "doc-1",
                "filename": "test.txt",
                "source": "",
            }
        ],
    }

    with (
        patch("app.agent.engine.get_llm", return_value=mock_llm),
        patch("app.agent.engine.rag_search", new_callable=AsyncMock) as mock_rag,
    ):
        mock_rag.return_value = mock_rag_result
        engine = AgentEngine()
        # Re-register the mocked tool
        engine._tools["rag_search"] = mock_rag

        events = []
        async for event in engine.run("What does the document say?"):
            events.append(event)

    types = [e["type"] for e in events]
    assert "thought" in types
    assert "action" in types
    assert "observation" in types
    assert "answer" in types


@pytest.mark.asyncio
async def test_engine_unknown_tool() -> None:
    """Agent handles unknown tool gracefully."""
    call_count = 0

    async def mock_ainvoke(messages: list) -> AsyncMock:
        nonlocal call_count
        call_count += 1
        result = AsyncMock()
        if call_count == 1:
            result.content = 'ACTION: {"tool": "nonexistent", "args": {}}'
        else:
            result.content = "I couldn't find that tool."
        return result

    mock_llm = AsyncMock()
    mock_llm.ainvoke = mock_ainvoke

    with patch("app.agent.engine.get_llm", return_value=mock_llm):
        engine = AgentEngine()

    events = []
    async for event in engine.run("Use a fake tool"):
        events.append(event)

    observations = [e for e in events if e["type"] == "observation"]
    assert len(observations) == 1
    assert "Unknown tool" in observations[0]["content"]
