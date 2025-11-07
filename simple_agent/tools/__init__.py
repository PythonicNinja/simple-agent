"""Tool registry."""

from __future__ import annotations

from typing import List, TYPE_CHECKING

from .base import Tool
from .file_read_tool import FileReadTool
from .math_tool import MathTool
from .python_tool import PythonSandboxTool
from .time_tool import TimeTool

if TYPE_CHECKING:  # pragma: no cover
    from ..config import Settings


def load_default_tools(settings: "Settings | None" = None) -> List[Tool]:
    """Return the default toolset used by the CLI."""

    allowed_imports = None
    if settings and settings.python_tool_imports:
        allowed_imports = set(settings.python_tool_imports)

    return [
        TimeTool(),
        MathTool(),
        FileReadTool(),
        PythonSandboxTool(extra_allowed_imports=allowed_imports),
    ]


__all__ = ["Tool", "load_default_tools"]
