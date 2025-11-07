"""Tool protocol definitions."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


class Tool(Protocol):
    """Minimal surface required for a tool."""

    name: str
    description: str

    def run(self, query: str) -> str:
        """Execute the tool."""


@dataclass(slots=True)
class SimpleTool:
    """Helper mixin that stores name/description."""

    name: str
    description: str
