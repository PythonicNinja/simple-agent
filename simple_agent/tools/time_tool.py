"""Current time tool."""

from __future__ import annotations

from datetime import datetime, timezone

from .base import SimpleTool


class TimeTool(SimpleTool):
    """Returns the current UTC timestamp."""

    def __init__(self) -> None:
        super().__init__(name="time", description="Returns the current UTC time in ISO-8601 format.")

    def run(self, _: str) -> str:
        return datetime.now(tz=timezone.utc).isoformat()
