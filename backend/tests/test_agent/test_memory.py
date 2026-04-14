"""Tests for conversation memory."""

from __future__ import annotations

from app.agent.memory import ConversationMemory


def test_add_and_get_messages() -> None:
    """Memory stores and retrieves messages correctly."""
    memory = ConversationMemory()
    memory.add_message("user", "Hello")
    memory.add_message("assistant", "Hi there!")

    messages = memory.get_messages()
    assert len(messages) == 2
    assert messages[0] == {"role": "user", "content": "Hello"}
    assert messages[1] == {"role": "assistant", "content": "Hi there!"}


def test_max_messages_limit() -> None:
    """Memory truncates to max_messages when exceeded."""
    memory = ConversationMemory(max_messages=3)
    for i in range(5):
        memory.add_message("user", f"Message {i}")

    messages = memory.get_messages()
    assert len(messages) == 3
    assert messages[0]["content"] == "Message 2"


def test_clear() -> None:
    """Memory clears all messages."""
    memory = ConversationMemory()
    memory.add_message("user", "Hello")
    memory.clear()
    assert memory.get_messages() == []
