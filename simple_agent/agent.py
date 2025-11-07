"""Core orchestration logic for the simple agent."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List

from .backends.base import LLMBackend
from .tools.base import Tool

SYSTEM_PROMPT_TEMPLATE = """{user_prompt}

You have access to the following tools:
{tool_descriptions}

If a tool is necessary, respond with ONLY a JSON object that looks like:
{{"tool": "<tool name>", "input": "<plain text request for the tool>"}}
Do not wrap the JSON in backticks or add commentary.
If no tool is needed, answer the user directly in natural language."""


@dataclass(slots=True)
class SimpleAgent:
    """Minimal tool-using agent with pluggable backends."""

    backend: LLMBackend
    tools: Iterable[Tool]
    system_prompt: str
    tool_map: Dict[str, Tool] = field(init=False)
    _prepared_system_prompt: str = field(init=False)

    def __post_init__(self) -> None:
        self.tool_map: Dict[str, Tool] = {tool.name: tool for tool in self.tools}
        descriptions = "\n".join(f"- {tool.name}: {tool.description}" for tool in self.tools) or "- (no tools available)"
        self._prepared_system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
            user_prompt=self.system_prompt,
            tool_descriptions=descriptions,
        )

    def run(self, user_input: str, max_turns: int = 5) -> str:
        history: List[dict[str, str]] = [
            {"role": "system", "content": self._prepared_system_prompt},
            {"role": "user", "content": user_input.strip()},
        ]

        for _ in range(max_turns):
            response = self.backend.generate(history)
            tool_request = self._maybe_extract_tool_request(response)
            if not tool_request:
                return response.strip()

            tool_name = tool_request.get("tool")
            tool_input = tool_request.get("input", "")

            tool = self.tool_map.get(tool_name or "")
            if not tool:
                history.append(
                    {
                        "role": "user",
                        "content": f"[Tool error] '{tool_name}' is not a known tool. Try responding to the user instead.",
                    }
                )
                continue

            tool_output = tool.run(tool_input)

            history.append({"role": "assistant", "content": json.dumps(tool_request)})
            history.append(
                {"role": "user", "content": f"[Tool:{tool_name}] {tool_output}"},
            )

        raise RuntimeError("Agent hit the maximum tool loop depth without producing an answer.")

    @staticmethod
    def _maybe_extract_tool_request(text: str) -> dict | None:
        """Attempt to parse a JSON tool request out of a model response."""

        text = text.strip()
        candidates = [text]

        fenced = re.findall(r"```(?:json)?\s*(.*?)```", text, flags=re.DOTALL)
        candidates.extend(content.strip() for content in fenced if content.strip())

        for candidate in candidates:
            try:
                data = json.loads(candidate)
            except json.JSONDecodeError:
                continue

            if isinstance(data, dict) and "tool" in data:
                return data

        return None
