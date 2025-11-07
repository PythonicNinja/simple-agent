"""Tool registry."""

from __future__ import annotations

from typing import List

from .base import Tool
from .file_read_tool import FileReadTool
from .math_tool import MathTool
from .time_tool import TimeTool


def load_default_tools() -> List[Tool]:
    """Return the default toolset used by the CLI."""

    return [TimeTool(), MathTool(), FileReadTool()]


__all__ = ["Tool", "load_default_tools"]
