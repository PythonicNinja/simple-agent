"""Sandboxed Python execution tool."""

from __future__ import annotations

import subprocess
from textwrap import dedent

from .base import SimpleTool


class PythonSandboxTool(SimpleTool):
    """Executes small Python snippets in a separate interpreter."""

    def __init__(self, *, timeout: int = 5) -> None:
        super().__init__(
            name="python",
            description="Run Python code in a sandboxed interpreter. Provide raw code; stdout is returned.",
        )
        self.timeout = timeout

    def run(self, query: str) -> str:
        code = query.strip()
        if not code:
            return "Provide Python code to run."

        wrapped = dedent(
            f"""
            import sys

            namespace = {{}}
            code = {code!r}
            try:
                exec(code, namespace, namespace)
            except SystemExit as exc:
                print(f"[SystemExit] {{exc}}", file=sys.stderr)
            except Exception as exc:  # pylint: disable=broad-except
                print(f"[Error] {{exc}}", file=sys.stderr)
            """
        ).strip()

        try:
            completed = subprocess.run(
                ["python3", "-c", wrapped],
                capture_output=True,
                text=True,
                timeout=self.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            return "Python execution timed out."
        except Exception as exc:  # pylint: disable=broad-except
            return f"Failed to invoke python: {exc}"

        stdout = completed.stdout.strip()
        stderr = completed.stderr.strip()

        if completed.returncode != 0 and stderr:
            return f"Python exited with {completed.returncode}: {stderr}"

        if stderr and stdout:
            return f"{stdout}\n[stderr]\n{stderr}"
        if stderr:
            return f"[stderr]\n{stderr}"
        return stdout or "(no output)"
