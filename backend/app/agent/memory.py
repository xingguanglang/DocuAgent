"""Conversation memory management for the agent."""

from __future__ import annotations


class ConversationMemory:
    """Manages conversation history and context window for the agent.

    Handles message storage, context truncation, and summary generation
    for long conversations.
    """

    def __init__(self, max_messages: int = 50) -> None:
        """Initialize conversation memory.

        Args:
            max_messages: Maximum messages to keep in active context.
        """
        self.max_messages = max_messages
        self._messages: list[dict[str, str]] = []

    def add_message(self, role: str, content: str) -> None:
        """Add a message to conversation history.

        Args:
            role: Message role ('user' or 'assistant').
            content: Message content.
        """
        self._messages.append({"role": role, "content": content})
        if len(self._messages) > self.max_messages:
            self._messages = self._messages[-self.max_messages :]

    def get_messages(self) -> list[dict[str, str]]:
        """Return current conversation history.

        Returns:
            List of message dicts with role and content.
        """
        return list(self._messages)

    def clear(self) -> None:
        """Clear all conversation history."""
        self._messages.clear()
