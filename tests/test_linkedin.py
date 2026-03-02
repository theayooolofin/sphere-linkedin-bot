import unittest
from dataclasses import dataclass

import requests

from linkedin_bot.linkedin import (
    LINKEDIN_MAX_POST_LENGTH,
    LinkedInPostError,
    build_post_payload,
    normalize_member_id,
    post_to_linkedin,
)


@dataclass
class FakeResponse:
    status_code: int
    text: str
    headers: dict[str, str]


class FakeSession:
    def __init__(self, outcomes):
        self.outcomes = list(outcomes)
        self.calls = 0

    def post(self, *_args, **_kwargs):
        self.calls += 1
        outcome = self.outcomes.pop(0)
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class LinkedInTests(unittest.TestCase):
    def test_normalize_member_id(self) -> None:
        self.assertEqual(normalize_member_id("urn:li:person:abc"), "abc")
        self.assertEqual(normalize_member_id("urn:li:member:def"), "def")
        self.assertEqual(normalize_member_id("xyz"), "xyz")

    def test_build_post_payload_truncates_text(self) -> None:
        content = "x" * (LINKEDIN_MAX_POST_LENGTH + 10)
        payload = build_post_payload(content, "urn:li:person:123")
        final_text = payload["specificContent"]["com.linkedin.ugc.ShareContent"][
            "shareCommentary"
        ]["text"]
        self.assertLessEqual(len(final_text), LINKEDIN_MAX_POST_LENGTH)
        self.assertTrue(final_text.endswith("..."))

    def test_post_to_linkedin_retries_retryable_status(self) -> None:
        session = FakeSession(
            [
                FakeResponse(429, "rate limit", {}),
                FakeResponse(201, "ok", {"x-restli-id": "urn:li:ugcPost:1"}),
            ]
        )
        response = post_to_linkedin(
            access_token="token",
            post_payload=build_post_payload("hello", "123"),
            timeout_seconds=1,
            max_retries=3,
            initial_retry_delay_seconds=0,
            session=session,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(session.calls, 2)

    def test_post_to_linkedin_raises_after_non_retryable_status(self) -> None:
        session = FakeSession([FakeResponse(401, "unauthorized", {})])
        with self.assertRaises(LinkedInPostError):
            post_to_linkedin(
                access_token="token",
                post_payload=build_post_payload("hello", "123"),
                timeout_seconds=1,
                max_retries=2,
                initial_retry_delay_seconds=0,
                session=session,
            )

    def test_post_to_linkedin_retries_request_exception(self) -> None:
        session = FakeSession(
            [
                requests.Timeout("timeout"),
                FakeResponse(201, "ok", {"x-restli-id": "urn:li:ugcPost:2"}),
            ]
        )
        response = post_to_linkedin(
            access_token="token",
            post_payload=build_post_payload("hello", "123"),
            timeout_seconds=1,
            max_retries=2,
            initial_retry_delay_seconds=0,
            session=session,
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(session.calls, 2)


if __name__ == "__main__":
    unittest.main()
