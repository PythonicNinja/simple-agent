"""Sandboxed Python execution tool."""

from __future__ import annotations

import subprocess
import ast
from textwrap import dedent

from .base import SimpleTool


class PythonSandboxTool(SimpleTool):
    """Executes small Python snippets in a separate interpreter."""

    def __init__(
        self,
        *,
        timeout: int = 5,
        extra_allowed_imports: set[str] | None = None,
    ) -> None:
        super().__init__(
            name="python",
            description="Run Python code in a sandboxed interpreter. Provide raw code; stdout is returned.",
        )
        self.timeout = timeout
        default_allowed = {
            "math",
            "statistics",
            "datetime",
            "time",
            "random",
            "json",
            "collections",
            "itertools",
            "functools",
            "os",
            "sys",
            "pathlib",
            "psutil",
        }
        self.allowed_imports = default_allowed | (extra_allowed_imports or set())

    def run(self, query: str) -> str:
        code = query.strip()
        if not code:
            return "Provide Python code to run."

        disallowed = _find_disallowed_imports(code, self.allowed_imports)
        if disallowed:
            allowed = ", ".join(sorted(self.allowed_imports))
            return f"Imports not permitted: {', '.join(sorted(disallowed))}. Allowed modules: {allowed}."

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


def _find_disallowed_imports(code: str, allowed: set[str]) -> set[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return set()

    blocked: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                root = alias.name.split(".")[0]
                if root not in allowed:
                    blocked.add(root)
        elif isinstance(node, ast.ImportFrom):
            if node.module is None or node.level:
                blocked.add("<relative>")
                continue
            root = node.module.split(".")[0]
            if root not in allowed:
                blocked.add(root)
    return blocked
