from __future__ import annotations

import logging
import os

from linkedin_bot.config import BotConfig, ConfigError
from linkedin_bot.content import generate_post
from linkedin_bot.linkedin import LinkedInPostError, build_post_payload, post_to_linkedin

logger = logging.getLogger(__name__)


def configure_logging() -> None:
    log_level = os.getenv("LOG_LEVEL", "INFO").strip().upper() or "INFO"
    logging.basicConfig(
        level=log_level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
    )


def run(config: BotConfig | None = None) -> int:
    cfg = config or BotConfig.from_env()

    content = generate_post(
        api_key=cfg.gemini_api_key,
        model=cfg.gemini_model,
        prompt=cfg.prompt,
        timeout_seconds=cfg.gemini_timeout_seconds,
        max_retries=cfg.max_retries,
        initial_retry_delay_seconds=cfg.initial_retry_delay_seconds,
    )

    payload = build_post_payload(content=content, raw_member_id=cfg.linkedin_person_urn)
    response = post_to_linkedin(
        access_token=cfg.linkedin_access_token,
        post_payload=payload,
        timeout_seconds=cfg.linkedin_timeout_seconds,
        max_retries=cfg.max_retries,
        initial_retry_delay_seconds=cfg.initial_retry_delay_seconds,
    )

    logger.info(
        "LinkedIn post published. status=%s post_urn=%s",
        response.status_code,
        response.headers.get("x-restli-id", "unknown"),
    )
    return 0


def main() -> int:
    configure_logging()
    try:
        return run()
    except ConfigError as exc:
        logger.error("Configuration error: %s", exc)
    except LinkedInPostError as exc:
        logger.error("LinkedIn publish failed: %s", exc)
        if exc.response_body:
            logger.error("LinkedIn response body: %s", exc.response_body)
    except Exception:
        logger.exception("Unexpected failure while running bot.")
    return 1
