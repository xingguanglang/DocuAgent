"""SQL query tool for the agent."""

from __future__ import annotations

from typing import Any


async def execute_sql(query: str) -> dict[str, Any]:
    """Execute a read-only SQL query against the database.

    Only SELECT statements are allowed for safety.

    Args:
        query: SQL SELECT query to execute.

    Returns:
        Dict with column names and row data.

    Raises:
        ValueError: If the query is not a SELECT statement.
    """
    # TODO: Implement read-only SQL execution with proper sanitization
    raise NotImplementedError
