from __future__ import annotations

import logging
import time
from typing import Any

import requests
from requests import Response

logger = logging.getLogger(__name__)

LINKEDIN_UGC_POST_URL = "https://api.linkedin.com/v2/ugcPosts"
LINKEDIN_MAX_POST_LENGTH = 3000
RETRYABLE_STATUS_CODES = {408, 425, 429, 500, 502, 503, 504}


class LinkedInPostError(RuntimeError):
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


def normalize_member_id(raw_id: str) -> str:
    clean_id = str(raw_id).strip()
    if not clean_id:
        raise ValueError("LinkedIn member id cannot be empty.")

    for prefix in ("urn:li:person:", "urn:li:member:"):
        if clean_id.startswith(prefix):
            clean_id = clean_id[len(prefix) :]
            break

    clean_id = clean_id.strip()
    if not clean_id:
        raise ValueError("LinkedIn member id cannot be empty after normalization.")
    return clean_id


def _normalize_post_text(content: str) -> str:
    text = str(content).strip()
    if not text:
        raise ValueError("LinkedIn post content cannot be empty.")

    if len(text) <= LINKEDIN_MAX_POST_LENGTH:
        return text

    return text[: LINKEDIN_MAX_POST_LENGTH - 3].rstrip() + "..."


def build_post_payload(content: str, raw_member_id: str) -> dict[str, Any]:
    member_id = normalize_member_id(raw_member_id)
    post_text = _normalize_post_text(content)

    return {
        "author": f"urn:li:person:{member_id}",
        "lifecycleState": "PUBLISHED",
        "specificContent": {
            "com.linkedin.ugc.ShareContent": {
                "shareCommentary": {"text": post_text},
                "shareMediaCategory": "NONE",
            }
        },
        "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
    }


def post_to_linkedin(
    access_token: str,
    post_payload: dict[str, Any],
    timeout_seconds: float,
    max_retries: int,
    initial_retry_delay_seconds: float,
    *,
    session: Any | None = None,
) -> Response:
    if not str(access_token).strip():
        raise ValueError("LinkedIn access token is required.")
    if max_retries < 1:
        raise ValueError("max_retries must be at least 1.")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Restli-Protocol-Version": "2.0.0",
        "Content-Type": "application/json",
    }
    http = session or requests

    for attempt in range(1, max_retries + 1):
        try:
            response = http.post(
                LINKEDIN_UGC_POST_URL,
                headers=headers,
                json=post_payload,
                timeout=timeout_seconds,
            )
        except requests.RequestException as exc:
            if attempt >= max_retries:
                raise LinkedInPostError(
                    "LinkedIn request failed after all retries.",
                    response_body=str(exc),
                ) from exc

            delay_seconds = initial_retry_delay_seconds * (2 ** (attempt - 1))
            logger.warning(
                "LinkedIn request error on attempt %s/%s; retrying in %.1f seconds.",
                attempt,
                max_retries,
                delay_seconds,
                exc_info=True,
            )
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            continue

        if response.status_code == 201:
            return response

        if response.status_code in RETRYABLE_STATUS_CODES and attempt < max_retries:
            delay_seconds = initial_retry_delay_seconds * (2 ** (attempt - 1))
            logger.warning(
                "LinkedIn returned retryable status %s on attempt %s/%s; retrying in %.1f seconds.",
                response.status_code,
                attempt,
                max_retries,
                delay_seconds,
            )
            if delay_seconds > 0:
                time.sleep(delay_seconds)
            continue

        raise LinkedInPostError(
            f"LinkedIn post failed with status {response.status_code}.",
            status_code=response.status_code,
            response_body=response.text,
        )

    raise LinkedInPostError("LinkedIn request failed after all retries.")
