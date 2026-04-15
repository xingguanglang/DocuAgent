"""Tests for the sandboxed code execution tool."""

from __future__ import annotations

import pytest

from app.agent.tools.code_executor import _check_code_safety, execute_code


class TestCodeSafetyCheck:
    """Tests for static code safety validation."""

    def test_safe_code_passes(self):
        assert _check_code_safety("print('hello')") is None

    def test_safe_math_passes(self):
        assert _check_code_safety("x = 1 + 2\nprint(x)") is None

    def test_blocks_os_import(self):
        result = _check_code_safety("import os")
        assert result is not None
        assert "os" in result

    def test_blocks_subprocess(self):
        result = _check_code_safety("import subprocess")
        assert result is not None
        assert "subprocess" in result

    def test_blocks_from_import(self):
        result = _check_code_safety("from os import path")
        assert result is not None

    def test_blocks_open(self):
        result = _check_code_safety("f = open('file.txt')")
        assert result is not None
        assert "open" in result

    def test_blocks_exec(self):
        result = _check_code_safety("exec('print(1)')")
        assert result is not None

    def test_blocks_eval(self):
        result = _check_code_safety("eval('1+1')")
        assert result is not None


@pytest.mark.asyncio
async def test_execute_simple_code():
    """Executing simple print code returns stdout."""
    result = await execute_code("print('hello world')")
    assert result["status"] == "success"
    assert "hello world" in result["stdout"]
    assert result["stderr"] == ""


@pytest.mark.asyncio
async def test_execute_math_code():
    """Executing math code returns correct output."""
    result = await execute_code("print(2 ** 10)")
    assert result["status"] == "success"
    assert "1024" in result["stdout"]


@pytest.mark.asyncio
async def test_execute_blocked_code():
    """Executing code with blocked imports returns blocked status."""
    result = await execute_code("import os\nprint(os.getcwd())")
    assert result["status"] == "blocked"
    assert "os" in result["stderr"]


@pytest.mark.asyncio
async def test_execute_syntax_error():
    """Executing invalid syntax returns error status."""
    result = await execute_code("def foo(\n")
    assert result["status"] == "error"
    assert result["stderr"] != ""


@pytest.mark.asyncio
async def test_unsupported_language():
    """Non-python language returns error."""
    result = await execute_code("console.log('hi')", language="javascript")
    assert result["status"] == "error"
    assert "not supported" in result["stderr"]
