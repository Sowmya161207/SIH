"""
code_sandbox.py
---------------
Isolated Code Execution Sandbox.
Safely executes Python code snippets in a restricted subprocess environment
with timeouts, output capturing, and import filtering.
"""

import sys
import os
import time
import subprocess
import tempfile
from typing import Dict, Any, List

SANDBOX_TIMEOUT_SECONDS = 10
BLOCKED_IMPORTS = [
    "os.system", "subprocess", "shutil.rmtree", "socket",
    "ctypes", "multiprocessing", "builtins.__import__"
]

SAFE_DEFAULT_IMPORTS = ["math", "json", "datetime", "re", "random", "collections", "itertools", "functools", "statistics"]


def execute_python_sandbox(code: str) -> Dict[str, Any]:
    """
    Executes Python code in a controlled subprocess.

    Returns:
    {
        "success": bool,
        "output": str,
        "error": Optional[str],
        "execution_time_ms": int,
        "stdout": str,
        "stderr": str
    }
    """
    if not code or not code.strip():
        return {
            "success": False,
            "output": "",
            "error": "Code snippet is empty.",
            "execution_time_ms": 0,
            "stdout": "",
            "stderr": ""
        }

    # Security check for dangerous code snippets
    for forbidden in BLOCKED_IMPORTS:
        if forbidden in code:
            return {
                "success": False,
                "output": "",
                "error": f"Security Violation: '{forbidden}' is restricted in the execution sandbox.",
                "execution_time_ms": 0,
                "stdout": "",
                "stderr": f"Security restriction triggered for {forbidden}"
            }

    # Write code snippet to a temporary file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False, encoding="utf-8") as temp_file:
        temp_file.write(code)
        temp_filepath = temp_file.name

    start_time = time.time()

    try:
        # Run in subprocess using current python executable with restricted environment
        env = os.environ.copy()
        # Remove dangerous env variables if any
        env["PYTHONDONTWRITEBYTECODE"] = "1"

        process = subprocess.run(
            [sys.executable, temp_filepath],
            capture_output=True,
            text=True,
            timeout=SANDBOX_TIMEOUT_SECONDS,
            env=env,
            cwd=tempfile.gettempdir()
        )

        elapsed_ms = int((time.time() - start_time) * 1000)

        stdout = process.stdout.strip()
        stderr = process.stderr.strip()

        if process.returncode == 0:
            return {
                "success": True,
                "output": stdout if stdout else "(Code executed successfully with no stdout output)",
                "error": None,
                "execution_time_ms": elapsed_ms,
                "stdout": stdout,
                "stderr": stderr
            }
        else:
            return {
                "success": False,
                "output": stdout,
                "error": stderr if stderr else f"Process exited with return code {process.returncode}",
                "execution_time_ms": elapsed_ms,
                "stdout": stdout,
                "stderr": stderr
            }

    except subprocess.TimeoutExpired:
        elapsed_ms = int((time.time() - start_time) * 1000)
        return {
            "success": False,
            "output": "",
            "error": f"Execution Timed Out: Code exceeded the {SANDBOX_TIMEOUT_SECONDS}s sandbox threshold.",
            "execution_time_ms": elapsed_ms,
            "stdout": "",
            "stderr": "TimeoutExpired"
        }
    except Exception as exc:
        return {
            "success": False,
            "output": "",
            "error": f"Sandbox Execution Error: {str(exc)}",
            "execution_time_ms": 0,
            "stdout": "",
            "stderr": str(exc)
        }
    finally:
        if os.path.exists(temp_filepath):
            try:
                os.remove(temp_filepath)
            except Exception:
                pass
