"""Google Gemini REST backend."""

from __future__ import annotations

import os
from typing import List

import requests

from .base import LLMBackend, Message


class GeminiBackend(LLMBackend):
    """Calls the Gemini `generateContent` endpoint through requests."""

    def __init__(
        self,
        api_key: str,
        model: str,
        *,
        timeout: float = 30,
        base_url: str | None = None,
    ) -> None:
        if not api_key:
            raise ValueError("GEMINI_API_KEY is required for the Gemini backend.")

        self.api_key = api_key
        self.model = model
        self.timeout = timeout
        self.base_url = base_url or os.getenv(
            "GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1"
        )

    def generate(self, messages: List[Message]) -> str:
        system_instruction = ""
        converted_messages = []

        for message in messages:
            role = message.get("role", "user")
            content = message.get("content", "")

            if role == "system":
                system_instruction = content
                continue

            converted_messages.append(
                {
                    "role": "user" if role == "user" else "model",
                    "parts": [{"text": content}],
                }
            )

        if system_instruction:
            if converted_messages:
                parts = converted_messages[0].get("parts") or []
                if not parts:
                    parts = [{"text": ""}]
                    converted_messages[0]["parts"] = parts
                parts[0]["text"] = f"{system_instruction}\n\n{parts[0].get('text', '')}".strip()
            else:
                converted_messages.append(
                    {
                        "role": "user",
                        "parts": [{"text": system_instruction}],
                    }
                )

        payload: dict = {"contents": converted_messages}

        try:
            response = requests.post(
                f"{self.base_url}/models/{self.model}:generateContent?key={self.api_key}",
                json=payload,
                timeout=self.timeout,
            )
        except requests.RequestException as exc:
            raise RuntimeError(f"Gemini request failed: {exc}") from exc
        try:
            response.raise_for_status()
        except requests.HTTPError as exc:
            detail = _extract_error_detail(response)
            raise RuntimeError(f"Gemini request failed: {detail}") from exc
        data = response.json()

        try:
            candidates = data["candidates"]
            first = candidates[0]
            part = first["content"]["parts"][0]
            return part["text"].strip()
        except (KeyError, IndexError, TypeError) as exc:
            raise RuntimeError(f"Unexpected response from Gemini: {data}") from exc


def _extract_error_detail(response: requests.Response) -> str:
    try:
        payload = response.json()
        if isinstance(payload, dict):
            if "error" in payload:
                if isinstance(payload["error"], dict) and "message" in payload["error"]:
                    return str(payload["error"]["message"])
                return str(payload["error"])
        return str(payload)
    except ValueError:
        return response.text or response.reason or "Unknown error"
