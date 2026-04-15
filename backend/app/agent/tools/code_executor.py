"""Sandboxed code execution tool for the agent."""

from __future__ import annotations

import asyncio
import logging
import subprocess
import sys
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)

# Safety limits
MAX_EXECUTION_TIME_SECONDS = 10
MAX_OUTPUT_LENGTH = 5000

# Dangerous modules / built-ins that should not be importable
BLOCKED_IMPORTS = frozenset(
    {
        "os",
        "subprocess",
        "shutil",
        "sys",
        "importlib",
        "ctypes",
        "socket",
        "http",
        "urllib",
        "requests",
        "pathlib",
        "glob",
        "signal",
        "multiprocessing",
        "threading",
        "pickle",
        "shelve",
        "code",
        "compile",
        "exec",
        "eval",
        "__import__",
    }
)


def _check_code_safety(code: str) -> str | None:
    """Check code for dangerous patterns.

    Args:
        code: Source code to check.

    Returns:
        Error message if unsafe, None if safe.
    """
    for blocked in BLOCKED_IMPORTS:
        # Check for "import os", "from os", "import  os" etc.
        if f"import {blocked}" in code or f"from {blocked}" in code:
            return f"Blocked: importing '{blocked}' is not allowed for security reasons."

    dangerous_builtins = ["open(", "exec(", "eval(", "compile(", "__import__"]
    for pattern in dangerous_builtins:
        if pattern in code:
            return f"Blocked: '{pattern.rstrip('(')}' is not allowed for security reasons."

    return None


async def execute_code(code: str, language: str = "python") -> dict[str, str]:
    """Execute code in a sandboxed subprocess with safety restrictions.

    The code is written to a temporary file and executed in a separate
    process with resource limits (timeout, no network, no file I/O).

    Args:
        code: Source code to execute.
        language: Programming language (currently only 'python' supported).

    Returns:
        Dict with stdout, stderr, and execution status.
    """
    if language != "python":
        return {
            "status": "error",
            "stdout": "",
            "stderr": f"Language '{language}' is not supported. Only 'python' is available.",
        }

    # Static safety check
    safety_error = _check_code_safety(code)
    if safety_error is not None:
        return {
            "status": "blocked",
            "stdout": "",
            "stderr": safety_error,
        }

    # Write code to temp file
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".py", delete=False
    ) as f:
        f.write(code)
        tmp_path = Path(f.name)

    try:
        # Execute in subprocess with timeout
        python_exe = sys.executable or "python"
        process = await asyncio.create_subprocess_exec(
            python_exe,
            str(tmp_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            # Limit environment — only expose PATH and HOME
            env={
                "PATH": str(Path(python_exe).parent) + ":/usr/bin:/usr/local/bin",
                "HOME": "/tmp",
            },
        )

        try:
            stdout_bytes, stderr_bytes = await asyncio.wait_for(
                process.communicate(),
                timeout=MAX_EXECUTION_TIME_SECONDS,
            )
        except TimeoutError:
            process.kill()
            await process.communicate()
            return {
                "status": "timeout",
                "stdout": "",
                "stderr": f"Execution timed out after {MAX_EXECUTION_TIME_SECONDS} seconds.",
            }

        stdout = stdout_bytes.decode("utf-8", errors="replace")[:MAX_OUTPUT_LENGTH]
        stderr = stderr_bytes.decode("utf-8", errors="replace")[:MAX_OUTPUT_LENGTH]

        status = "success" if process.returncode == 0 else "error"

        return {
            "status": status,
            "stdout": stdout,
            "stderr": stderr,
        }

    except Exception as e:
        logger.exception("Code execution failed")
        return {
            "status": "error",
            "stdout": "",
            "stderr": f"Execution error: {e!s}",
        }
    finally:
        # Clean up temp file
        tmp_path.unlink(missing_ok=True)
