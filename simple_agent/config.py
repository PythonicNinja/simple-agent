"""Environment driven configuration helpers."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from typing import Literal

from dotenv import load_dotenv

load_dotenv()


BackendName = Literal["chatgpt", "gemini"]


@dataclass(frozen=True, slots=True)
class Settings:
    """Typed view over the required runtime configuration."""

    backend: BackendName
    system_prompt: str
    openai_api_key: str | None
    openai_model: str
    gemini_api_key: str | None
    gemini_model: str
    request_timeout: float

    @staticmethod
    def _get_env(key: str, default: str | None = None) -> str | None:
        value = os.getenv(key, default)
        return value.strip() if isinstance(value, str) else value

    @classmethod
    def from_env(cls) -> "Settings":
        backend = cls._get_env("LLM_BACKEND", "chatgpt") or "chatgpt"
        backend_normalized = backend.lower()
        if backend_normalized not in {"chatgpt", "gemini"}:
            raise ValueError(f"Unsupported backend '{backend}'. Expected 'chatgpt' or 'gemini'.")

        return cls(
            backend=backend_normalized,  # type: ignore[arg-type]
            system_prompt=cls._get_env(
                "AGENT_SYSTEM_PROMPT",
                "You are a concise assistant. Use tools only when strictly necessary.",
            )
            or "You are a concise assistant. Use tools only when strictly necessary.",
            openai_api_key=cls._get_env("OPENAI_API_KEY"),
            openai_model=cls._get_env("OPENAI_MODEL", "gpt-4o-mini"),
            gemini_api_key=cls._get_env("GEMINI_API_KEY"),
            gemini_model=cls._get_env("GEMINI_MODEL", "gemini-1.5-flash"),
            request_timeout=float(cls._get_env("REQUEST_TIMEOUT", "30")),
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Convenience accessor with caching to avoid redundant parsing."""

    return Settings.from_env()
