"""OpenAI Chat Completions backend."""

from __future__ import annotations

import os
from typing import List

import requests

from .base import LLMBackend, Message


class ChatGPTBackend(LLMBackend):
    """Thin wrapper over the OpenAI Chat Completions API."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        timeout: float = 30,
        base_url: str | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("OPENAI_API_KEY is required for the ChatGPT backend.")

        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.base_url = base_url or os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    def generate(self, messages: List[Message]) -> str:
        payload = {
            "model": self.model,
            "messages": messages,
            "temperature": 0.2,
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"OpenAI request failed: {exc}") from exc
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            detail = _extract_error_detail(response)
            raise RuntimeError(f"OpenAI request failed: {detail}") from exc

        data = response.json()
        try:
            return data["choices"][0]["message"]["content"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected response from OpenAI: {data}") from exc


def _extract_error_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
        return payload.get("error", {}).get("message") or str(payload)
    except ValueError:
        return response.text or response.reason or "Unknown error"
