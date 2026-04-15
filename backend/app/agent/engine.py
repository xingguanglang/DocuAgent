"""ReAct Agent engine for autonomous tool selection and execution."""

from __future__ import annotations

import json
import logging
from collections.abc import AsyncGenerator
from typing import Any

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from app.agent.tools.rag_tool import rag_search
from app.services.llm_service import get_llm

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
You are DocuAgent, an intelligent document assistant. You help users find \
information from their uploaded documents.

You have access to the following tools:

1. **rag_search**: Search uploaded documents for relevant information.
   - Input: {"query": "search query", "top_k": 5}
   - Use this when the user asks a question that might be answered by their documents.

When you need to use a tool, respond with EXACTLY this JSON format on a single line:
ACTION: {"tool": "rag_search", "args": {"query": "...", "top_k": 5}}

After receiving tool results (in OBSERVATION), synthesize the information and \
provide a clear, helpful answer with citations. Reference specific documents \
and quote relevant passages when possible.

If no documents are found or the question cannot be answered from the documents, \
say so honestly and offer to help in other ways.

Always respond in the same language the user uses.\
"""

MAX_ITERATIONS = 5


class AgentEngine:
    """ReAct-style agent that reasons about which tools to use.

    The agent follows a Thought -> Action -> Observation loop,
    deciding at each step whether to use RAG retrieval, execute code,
    query a database, search the web, or produce a final answer.
    """

    def __init__(self) -> None:
        """Initialize the agent engine."""
        self._llm = get_llm()
        self._tools: dict[str, Any] = {
            "rag_search": rag_search,
        }

    async def run(
        self,
        query: str,
        conversation_history: list[dict[str, str]] | None = None,
    ) -> AsyncGenerator[dict[str, Any], None]:
        """Execute the agent loop and yield streaming events.

        Follows ReAct pattern: the LLM thinks, optionally calls a tool,
        observes the result, and either calls another tool or produces
        a final answer.

        Args:
            query: User's question or request.
            conversation_history: Previous messages for context.

        Yields:
            Event dicts with type (thought/action/observation/answer)
            and content.
        """
        messages: list[Any] = [SystemMessage(content=SYSTEM_PROMPT)]

        # Add conversation history if provided
        if conversation_history:
            for msg in conversation_history:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                elif msg["role"] == "assistant":
                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=query))

        for iteration in range(MAX_ITERATIONS):
            logger.info("Agent iteration %d", iteration + 1)

            # Ask LLM
            response = await self._llm.ainvoke(messages)
            response_text: str = (
                response.content
                if isinstance(response.content, str)
                else str(response.content)
            )

            # Check if response contains a tool call
            action_data = self._parse_action(response_text)

            if action_data is not None:
                # Extract the thought (text before ACTION:)
                action_idx = response_text.find("ACTION:")
                thought = response_text[:action_idx].strip() if action_idx > 0 else ""

                if thought:
                    yield {"type": "thought", "content": thought}

                tool_name = action_data.get("tool", "")
                tool_args = action_data.get("args", {})

                yield {
                    "type": "action",
                    "content": json.dumps(
                        {"tool": tool_name, **tool_args}, ensure_ascii=False
                    ),
                }

                # Execute the tool
                observation = await self._execute_tool(tool_name, tool_args)

                yield {
                    "type": "observation",
                    "content": observation
                    if len(observation) <= 500
                    else observation[:500] + "...",
                }

                # Feed observation back to the LLM
                messages.append(AIMessage(content=response_text))
                messages.append(
                    HumanMessage(content=f"OBSERVATION:\n{observation}")
                )
            else:
                # No tool call — this is the final answer
                yield {"type": "answer", "content": response_text}
                return

        # If we exhausted iterations, return whatever we have
        yield {
            "type": "answer",
            "content": "I've done extensive research but couldn't fully resolve your query. "
            "Please try rephrasing your question.",
        }

    def _parse_action(self, text: str) -> dict[str, Any] | None:
        """Parse an ACTION: JSON block from LLM response.

        Args:
            text: LLM response text.

        Returns:
            Parsed action dict or None if no action found.
        """
        marker = "ACTION:"
        idx = text.find(marker)
        if idx == -1:
            return None

        json_str = text[idx + len(marker) :].strip()

        # Find the JSON object boundaries
        brace_start = json_str.find("{")
        if brace_start == -1:
            return None

        depth = 0
        brace_end = -1
        for i, ch in enumerate(json_str[brace_start:], start=brace_start):
            if ch == "{":
                depth += 1
            elif ch == "}":
                depth -= 1
                if depth == 0:
                    brace_end = i + 1
                    break

        if brace_end == -1:
            return None

        try:
            return json.loads(json_str[brace_start:brace_end])
        except json.JSONDecodeError:
            logger.warning("Failed to parse action JSON: %s", json_str[:100])
            return None

    async def _execute_tool(
        self, tool_name: str, tool_args: dict[str, Any]
    ) -> str:
        """Execute a tool by name with given arguments.

        Args:
            tool_name: Name of the tool to execute.
            tool_args: Arguments to pass to the tool.

        Returns:
            Tool result as a formatted string.
        """
        tool_fn = self._tools.get(tool_name)
        if tool_fn is None:
            return f"Error: Unknown tool '{tool_name}'. Available tools: {list(self._tools.keys())}"

        try:
            result = await tool_fn(**tool_args)
            return json.dumps(result, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.exception("Tool '%s' failed", tool_name)
            return f"Error executing {tool_name}: {e!s}"
