"""Tests for the Python sandbox helper functions."""

from __future__ import annotations

from simple_agent.tools.python_tool import _find_disallowed_imports


def test_find_disallowed_imports_blocks_unknown_modules() -> None:
    code = "import math\nimport secrets\nfrom collections import Counter"
    blocked = _find_disallowed_imports(code, {"math", "collections"})

    assert blocked == {"secrets"}


def test_find_disallowed_imports_marks_relative_imports() -> None:
    code = "from . import helpers"

    blocked = _find_disallowed_imports(code, {"json"})

    assert "<relative>" in blocked
