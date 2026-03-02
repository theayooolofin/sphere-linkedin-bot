from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Mapping

DEFAULT_PROMPT = (
    "Write a short, punchy LinkedIn post about AI sales efficiency. "
    "Use lots of white space."
)


class ConfigError(ValueError):
    """Raised when required configuration is missing or invalid."""


def _get_required(environ: Mapping[str, str], key: str) -> str:
    value = environ.get(key, "").strip()
    if not value:
        raise ConfigError(f"Missing required environment variable: {key}")
    return value


def _get_float(
    environ: Mapping[str, str], key: str, default: float, minimum: float
) -> float:
    raw_value = environ.get(key)
    if raw_value is None:
        return default

    try:
        parsed = float(raw_value)
    except ValueError as exc:
        raise ConfigError(f"Environment variable {key} must be a number.") from exc

    if parsed < minimum:
        raise ConfigError(f"Environment variable {key} must be >= {minimum}.")
    return parsed


def _get_int(environ: Mapping[str, str], key: str, default: int, minimum: int) -> int:
    raw_value = environ.get(key)
    if raw_value is None:
        return default

    try:
        parsed = int(raw_value)
    except ValueError as exc:
        raise ConfigError(f"Environment variable {key} must be an integer.") from exc

    if parsed < minimum:
        raise ConfigError(f"Environment variable {key} must be >= {minimum}.")
    return parsed


@dataclass(frozen=True)
class BotConfig:
    gemini_api_key: str
    linkedin_access_token: str
    linkedin_person_urn: str
    gemini_model: str = "gemini-2.5-flash"
    prompt: str = DEFAULT_PROMPT
    gemini_timeout_seconds: float = 30.0
    linkedin_timeout_seconds: float = 30.0
    max_retries: int = 3
    initial_retry_delay_seconds: float = 2.0

    @classmethod
    def from_env(cls, environ: Mapping[str, str] | None = None) -> "BotConfig":
        env = os.environ if environ is None else environ
        prompt = env.get("POST_PROMPT", DEFAULT_PROMPT).strip() or DEFAULT_PROMPT
        model = env.get("GEMINI_MODEL", "gemini-2.5-flash").strip() or "gemini-2.5-flash"

        return cls(
            gemini_api_key=_get_required(env, "GEMINI_API_KEY"),
            linkedin_access_token=_get_required(env, "LINKEDIN_ACCESS_TOKEN"),
            linkedin_person_urn=_get_required(env, "LINKEDIN_PERSON_URN"),
            gemini_model=model,
            prompt=prompt,
            gemini_timeout_seconds=_get_float(
                env, "GEMINI_TIMEOUT_SECONDS", default=30.0, minimum=0.1
            ),
            linkedin_timeout_seconds=_get_float(
                env, "LINKEDIN_TIMEOUT_SECONDS", default=30.0, minimum=0.1
            ),
            max_retries=_get_int(env, "MAX_RETRIES", default=3, minimum=1),
            initial_retry_delay_seconds=_get_float(
                env, "INITIAL_RETRY_DELAY_SECONDS", default=2.0, minimum=0.0
            ),
        )
