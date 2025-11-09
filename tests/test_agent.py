"""Tests for the SimpleAgent orchestration logic."""

from __future__ import annotations

from typing import Iterable, List

import pytest

from simple_agent.agent import SimpleAgent, _truncate
from simple_agent.backends.base import LLMBackend, Message
from simple_agent.tools.base import SimpleTool, Tool


class DummyBackend(LLMBackend):
    """Backend that returns predefined responses for each call."""

    def __init__(self, responses: Iterable[str]) -> None:
        self._responses = list(responses)
        self.calls: List[List[Message]] = []

    def generate(self, messages: List[Message]) -> str:
        if not self._responses:
            raise AssertionError("DummyBackend has no more responses queued.")
        # Capture a shallow copy so tests can inspect the conversation.
        self.calls.append([msg.copy() for msg in messages])
        return self._responses.pop(0)


class RecordingTool(SimpleTool):
    """Tool that records the inputs it receives."""

    def __init__(self) -> None:
        super().__init__(name="echo", description="Echo the provided input.")
        self.invocations: list[str] = []

    def run(self, query: str) -> str:
        self.invocations.append(query)
        return f"tool ran with: {query}"


def _make_agent(responses: Iterable[str], tools: Iterable[Tool] = ()) -> tuple[SimpleAgent, DummyBackend]:
    backend = DummyBackend(responses)
    agent = SimpleAgent(backend=backend, tools=list(tools), system_prompt="Be helpful.")
    return agent, backend


def test_agent_returns_direct_response_without_tool_use() -> None:
    agent, backend = _make_agent(["  final answer  "])

    result = agent.run("Question?")

    assert result == "final answer"
    assert len(backend.calls) == 1
    assert backend.calls[0][0]["role"] == "system"


def test_agent_executes_requested_tool_and_returns_model_reply() -> None:
    tool = RecordingTool()
    agent, backend = _make_agent(
        responses=[
            '{"tool":"echo","input":"calculate pi"}',
            "Result is 3.14",
        ],
        tools=[tool],
    )

    result = agent.run("What is pi?", max_turns=2)

    assert result == "Result is 3.14"
    assert tool.invocations == ["calculate pi"]
    assert len(backend.calls) == 2
    # Ensure the second backend call contains the tool output in the history.
    assert backend.calls[1][-1]["content"].startswith("[Tool:echo] tool ran with: calculate pi")


@pytest.mark.parametrize(
    "text,expected",
    [
        ('{"tool":"echo","input":"test"}', {"tool": "echo", "input": "test"}),
        ("```json\n{\"tool\": \"echo\"}\n```", {"tool": "echo"}),
        ("Some text", None),
    ],
)
def test_maybe_extract_tool_request_variants(text: str, expected: dict | None) -> None:
    assert SimpleAgent._maybe_extract_tool_request(text) == expected  # type: ignore[arg-type]


def test_truncate_adds_ellipsis_when_text_is_long() -> None:
    text = "abc" * 200
    truncated = _truncate(text, limit=10)
    assert truncated.endswith("…")
    assert len(truncated) == 11
