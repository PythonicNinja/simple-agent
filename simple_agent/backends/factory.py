"""Backend factory helpers."""

from __future__ import annotations

from ..config import Settings
from .base import LLMBackend
from .chatgpt import ChatGPTBackend
from .gemini import GeminiBackend


def get_backend(settings: Settings) -> LLMBackend:
    """Instantiate the backend described by the provided settings."""

    if settings.backend == "chatgpt":
        return ChatGPTBackend(
            api_key=settings.openai_api_key or "",
            model=settings.openai_model,
            timeout=settings.request_timeout,
        )

    if settings.backend == "gemini":
        return GeminiBackend(
            api_key=settings.gemini_api_key or "",
            model=settings.gemini_model,
            timeout=settings.request_timeout,
        )

    raise ValueError(f"Unsupported backend '{settings.backend}'.")
