"""Backend interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import List


Message = dict[str, str]


class LLMBackend(ABC):
    """Abstract language model backend."""

    @abstractmethod
    def generate(self, messages: List[Message]) -> str:
        """Return the assistant content for the given chat history."""

        raise NotImplementedError
