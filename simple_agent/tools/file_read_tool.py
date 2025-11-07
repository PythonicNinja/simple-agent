"""Tool for reading snippets of local files safely."""

from __future__ import annotations

from pathlib import Path

from .base import SimpleTool


class FileReadTool(SimpleTool):
    """Reads text files relative to the repo, optionally with a line range."""

    def __init__(self, base_dir: Path | None = None, *, max_chars: int = 4000) -> None:
        super().__init__(
            name="file_reader",
            description="Read a local text file. Format: 'path/to/file[:start-end]'.",
        )
        self.base_dir = Path(base_dir or Path.cwd()).resolve()
        self.max_chars = max_chars

    def run(self, query: str) -> str:
        query = query.strip()
        if not query:
            return "Provide a relative path, optionally with :start-end for line numbers."

        path_str, sep, range_str = query.partition(":")
        target = (self.base_dir / path_str).resolve()

        if not str(target).startswith(str(self.base_dir)):
            return "Refusing to read outside the project directory."
        if not target.exists():
            return f"File not found: {path_str}"
        if target.is_dir():
            return f"'{path_str}' is a directory."

        try:
            text = target.read_text(encoding="utf-8", errors="replace")
        except UnicodeDecodeError:
            return "File does not appear to be UTF-8 text."

        lines = text.splitlines()
        snippet: str

        if sep:
            start_line, end_line = _parse_range(range_str)
            if start_line is None:
                return "Invalid range. Use integers like :10-30."
            start_idx = max(start_line - 1, 0)
            end_idx = end_line if end_line is not None else start_idx + 40
            snippet_lines = lines[start_idx:end_idx]
            snippet = "\n".join(snippet_lines)
        else:
            snippet = "\n".join(lines[:80])

        snippet = snippet.strip()
        if len(snippet) > self.max_chars:
            snippet = f"{snippet[: self.max_chars]}…"

        return f"{path_str}:\n{snippet or '(file empty)'}"


def _parse_range(range_str: str) -> tuple[int | None, int | None]:
    if not range_str:
        return None, None
    parts = range_str.split("-")
    if len(parts) == 1:
        try:
            start = int(parts[0])
        except ValueError:
            return None, None
        return start, start + 40

    start_str, end_str = parts[0], parts[1]
    try:
        start = int(start_str) if start_str else 1
    except ValueError:
        return None, None
    if end_str:
        try:
            end = int(end_str)
        except ValueError:
            return None, None
    else:
        end = start + 40

    return start, end
