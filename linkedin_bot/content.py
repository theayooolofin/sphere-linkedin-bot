from __future__ import annotations

import logging
import time
from typing import Any

import requests

logger = logging.getLogger(__name__)
RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}

GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


class GeminiGenerationError(RuntimeError):
    def __init__(
        self,
        message: str,
        *,
        status_code: int | None = None,
        response_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.response_body = response_body


def _build_generate_content_url(model: str) -> str:
    clean_model = model.strip()
    if not clean_model:
        raise ValueError("Gemini model cannot be empty.")
    model_resource = clean_model if clean_model.startswith("models/") else f"models/{clean_model}"
    return f"{GEMINI_BASE_URL}/{model_resource}:generateContent"


def _extract_generated_text(payload: dict[str, Any]) -> str:
    candidates = payload.get("candidates")
    if not isinstance(candidates, list) or not candidates:
        raise ValueError("Gemini response has no candidates.")

    first_candidate = candidates[0]
    content = first_candidate.get("content") if isinstance(first_candidate, dict) else None
    parts = content.get("parts") if isinstance(content, dict) else None
    if not isinstance(parts, list):
        raise ValueError("Gemini response has no content parts.")

    chunks = []
    for part in parts:
        if isinstance(part, dict) and isinstance(part.get("text"), str):
            chunks.append(part["text"])

    text = "\n".join(chunks).strip()
    if not text:
        raise ValueError("Gemini generated an empty post.")
    return text


def generate_post(
    api_key: str,
    model: str,
    prompt: str,
    timeout_seconds: float,
    max_retries: int,
    initial_retry_delay_seconds: float,
    *,
    session: Any | None = None,
) -> str:
    if not str(api_key).strip():
        raise ValueError("Gemini API key is required.")
    if max_retries < 1:
        raise ValueError("max_retries must be at least 1.")

    url = _build_generate_content_url(model)
    headers = {
        "x-goog-api-key": api_key,
        "Content-Type": "application/json",
    }
    body = {"contents": [{"role": "user", "parts": [{"text": prompt}]}]}
    http = session or requests

    for attempt in range(1, max_retries + 1):
        try:
            response = http.post(
                url,
                headers=headers,
                json=body,
                timeout=timeout_seconds,
            )
        except requests.RequestException as exc:
            if attempt >= max_retries:
                raise GeminiGenerationError(
                    "Gemini request failed after all retries.",
                    response_body=str(exc),
                ) from exc

            delay_seconds = initial_retry_delay_seconds * (2 ** (attempt - 1))
            logger.warning(
                "Gemini request error on attempt %s/%s; retrying in %.1f seconds.",
                attempt,
                max_retries,
                delay_seconds,
                exc_info=True,
            )
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            continue

        if 200 <= response.status_code < 300:
            try:
                payload = response.json()
            except ValueError as exc:
                raise GeminiGenerationError(
                    "Gemini returned a non-JSON response.",
                    status_code=response.status_code,
                    response_body=response.text,
                ) from exc
            return _extract_generated_text(payload)

        if response.status_code in RETRYABLE_STATUS_CODES and attempt < max_retries:
            delay_seconds = initial_retry_delay_seconds * (2 ** (attempt - 1))
            logger.warning(
                "Gemini returned retryable status %s on attempt %s/%s; retrying in %.1f seconds.",
                response.status_code,
                attempt,
                max_retries,
                delay_seconds,
            )
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            continue

        raise GeminiGenerationError(
            f"Gemini generation failed with status {response.status_code}.",
            status_code=response.status_code,
            response_body=response.text,
        )

    raise GeminiGenerationError("Gemini request failed after all retries.")
