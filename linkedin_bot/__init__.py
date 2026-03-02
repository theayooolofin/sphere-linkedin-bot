"""LinkedIn content bot package."""

from typing import Any

__all__ = ["main", "run"]


def run(*args: Any, **kwargs: Any) -> int:
    from linkedin_bot.runner import run as _run

    return _run(*args, **kwargs)


def main() -> int:
    from linkedin_bot.runner import main as _main

    return _main()
