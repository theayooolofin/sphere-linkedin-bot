import unittest
from dataclasses import dataclass

import requests

from linkedin_bot.content import GeminiGenerationError, generate_post


@dataclass
class FakeResponse:
    status_code: int
    payload: dict
    text: str = ""

    def json(self):
        return self.payload


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


def gemini_payload(text: str) -> dict:
    return {
        "candidates": [{"content": {"parts": [{"text": text}]}}],
    }


class GeneratePostTests(unittest.TestCase):
    def test_generate_post_success(self) -> None:
        session = FakeSession([FakeResponse(200, gemini_payload("  hello world  "))])
        post = generate_post(
            api_key="gm-key",
            model="gemini-2.5-flash",
            prompt="test prompt",
            timeout_seconds=10,
            max_retries=3,
            initial_retry_delay_seconds=0,
            session=session,
        )
        self.assertEqual(post, "hello world")
        self.assertEqual(session.calls, 1)

    def test_generate_post_retries_then_succeeds(self) -> None:
        session = FakeSession(
            [
                FakeResponse(429, {}, text="rate limit"),
                FakeResponse(200, gemini_payload("final copy")),
            ]
        )
        post = generate_post(
            api_key="gm-key",
            model="gemini-2.5-flash",
            prompt="test prompt",
            timeout_seconds=10,
            max_retries=3,
            initial_retry_delay_seconds=0,
            session=session,
        )
        self.assertEqual(post, "final copy")
        self.assertEqual(session.calls, 2)

    def test_generate_post_retries_request_exception(self) -> None:
        session = FakeSession(
            [
                requests.Timeout("timeout"),
                FakeResponse(200, gemini_payload("final copy")),
            ]
        )
        post = generate_post(
            api_key="gm-key",
            model="gemini-2.5-flash",
            prompt="test prompt",
            timeout_seconds=10,
            max_retries=2,
            initial_retry_delay_seconds=0,
            session=session,
        )
        self.assertEqual(post, "final copy")
        self.assertEqual(session.calls, 2)

    def test_generate_post_fails_when_empty(self) -> None:
        session = FakeSession([FakeResponse(200, gemini_payload("   "))])
        with self.assertRaises(ValueError):
            generate_post(
                api_key="gm-key",
                model="gemini-2.5-flash",
                prompt="test prompt",
                timeout_seconds=10,
                max_retries=1,
                initial_retry_delay_seconds=0,
                session=session,
            )

    def test_generate_post_non_retryable_status_raises(self) -> None:
        session = FakeSession([FakeResponse(401, {}, text="unauthorized")])
        with self.assertRaises(GeminiGenerationError):
            generate_post(
                api_key="gm-key",
                model="gemini-2.5-flash",
                prompt="test prompt",
                timeout_seconds=10,
                max_retries=2,
                initial_retry_delay_seconds=0,
                session=session,
            )


if __name__ == "__main__":
    unittest.main()
