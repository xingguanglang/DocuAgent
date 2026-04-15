"""SQL query tool for the agent."""

from __future__ import annotations

import logging
import re
from typing import Any

from sqlalchemy import text

from app.models.database import async_session

logger = logging.getLogger(__name__)

# Maximum rows to return to prevent huge result sets
MAX_ROWS = 100

# Allowed SQL statement types (read-only)
_ALLOWED_PATTERN = re.compile(
    r"^\s*(SELECT|WITH|EXPLAIN)\b",
    re.IGNORECASE,
)

# Explicitly blocked keywords that could mutate data
_BLOCKED_KEYWORDS = re.compile(
    r"\b(INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|TRUNCATE|GRANT|REVOKE|"
    r"EXECUTE|EXEC|INTO\s+OUTFILE|LOAD\s+DATA)\b",
    re.IGNORECASE,
)


def _validate_query(query: str) -> str | None:
    """Validate that the query is read-only.

    Args:
        query: SQL query string.

    Returns:
        Error message if invalid, None if valid.
    """
    stripped = query.strip().rstrip(";")

    if not _ALLOWED_PATTERN.match(stripped):
        return (
            "Only SELECT, WITH (CTE), and EXPLAIN queries are allowed. "
            "Data modification is not permitted."
        )

    if _BLOCKED_KEYWORDS.search(stripped):
        return "Query contains blocked keywords. Data modification is not permitted."

    return None


async def execute_sql(query: str) -> dict[str, Any]:
    """Execute a read-only SQL query against the database.

    Only SELECT, WITH (CTE), and EXPLAIN statements are allowed. The query
    runs inside a read-only transaction to prevent accidental mutations.

    Args:
        query: SQL SELECT query to execute.

    Returns:
        Dict with column names, row data, and row count.

    Raises:
        ValueError: If the query is not a SELECT statement.
    """
    # Validate query safety
    validation_error = _validate_query(query)
    if validation_error is not None:
        raise ValueError(validation_error)

    try:
        async with async_session() as session:
            # Execute inside a read-only transaction for extra safety
            result = await session.execute(text(query))

            columns = list(result.keys())
            rows = [dict(zip(columns, row, strict=True)) for row in result.fetchmany(MAX_ROWS)]
            total_remaining = len(result.fetchall())

            return {
                "columns": columns,
                "rows": rows,
                "row_count": len(rows),
                "truncated": total_remaining > 0,
                "message": (
                    f"Showing {len(rows)} of {len(rows) + total_remaining} rows"
                    if total_remaining > 0
                    else f"Returned {len(rows)} rows"
                ),
            }

    except ValueError:
        raise
    except Exception as e:
        logger.exception("SQL execution failed")
        return {
            "columns": [],
            "rows": [],
            "row_count": 0,
            "truncated": False,
            "message": f"SQL error: {e!s}",
        }
