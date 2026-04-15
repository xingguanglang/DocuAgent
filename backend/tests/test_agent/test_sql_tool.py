"""Tests for the SQL query tool."""

from __future__ import annotations

import pytest

from app.agent.tools.sql_tool import _validate_query, execute_sql


class TestQueryValidation:
    """Tests for SQL query validation."""

    def test_select_allowed(self):
        assert _validate_query("SELECT * FROM users") is None

    def test_select_with_where(self):
        assert _validate_query("SELECT id, name FROM users WHERE id = '1'") is None

    def test_with_cte_allowed(self):
        assert _validate_query("WITH cte AS (SELECT 1) SELECT * FROM cte") is None

    def test_explain_allowed(self):
        assert _validate_query("EXPLAIN SELECT * FROM users") is None

    def test_insert_blocked(self):
        result = _validate_query("INSERT INTO users (name) VALUES ('test')")
        assert result is not None

    def test_update_blocked(self):
        result = _validate_query("UPDATE users SET name = 'test'")
        assert result is not None

    def test_delete_blocked(self):
        result = _validate_query("DELETE FROM users WHERE id = '1'")
        assert result is not None

    def test_drop_blocked(self):
        result = _validate_query("DROP TABLE users")
        assert result is not None

    def test_alter_blocked(self):
        result = _validate_query("ALTER TABLE users ADD COLUMN age INT")
        assert result is not None

    def test_truncate_blocked(self):
        result = _validate_query("TRUNCATE TABLE users")
        assert result is not None

    def test_random_text_blocked(self):
        result = _validate_query("hello world")
        assert result is not None


@pytest.mark.asyncio
async def test_execute_select_query():
    """Executing a SELECT on the users table returns results."""
    result = await execute_sql("SELECT COUNT(*) AS cnt FROM users")
    assert "columns" in result
    assert "rows" in result
    assert result["row_count"] >= 0


@pytest.mark.asyncio
async def test_execute_blocked_query():
    """Executing a mutation query raises ValueError."""
    with pytest.raises(ValueError, match="not permitted"):
        await execute_sql("INSERT INTO users (email) VALUES ('x@test.com')")


@pytest.mark.asyncio
async def test_execute_invalid_sql():
    """Executing invalid SQL returns error message."""
    result = await execute_sql("SELECT * FROM nonexistent_table_xyz")
    assert "error" in result["message"].lower() or result["row_count"] == 0
