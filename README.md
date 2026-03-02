# Sphere LinkedIn Bot

Automates daily LinkedIn text posts using Gemini for copy generation and the LinkedIn UGC API for publishing.

## What this does

1. Loads configuration from environment variables.
2. Generates a post with Gemini (`gemini-2.5-flash` by default).
3. Publishes it to your LinkedIn profile (`/v2/ugcPosts`).
4. Retries transient failures with exponential backoff.

## Project layout

- `bot.py`: Backward-compatible entrypoint (`python bot.py`).
- `linkedin_bot/config.py`: Environment parsing and validation.
- `linkedin_bot/content.py`: Gemini prompt execution and retries.
- `linkedin_bot/linkedin.py`: LinkedIn payload creation and publishing.
- `linkedin_bot/runner.py`: End-to-end runtime orchestration.
- `tests/`: Unit tests for config, generation, and publishing logic.

## Prerequisites

- Python 3.11+
- LinkedIn API access token with permission to publish posts
- Gemini API key

## Setup (local)

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Set required environment variables:

```powershell
$env:GEMINI_API_KEY="..."
$env:LINKEDIN_ACCESS_TOKEN="..."
$env:LINKEDIN_PERSON_URN="urn:li:person:123456789"
```

Run the bot:

```bash
python bot.py
```

## Schedule daily on Windows (no GitHub Actions)

Create a `.env` file in the repo root (copy from `.env.example`) and fill in:

- `GEMINI_API_KEY`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_URN`

Install a local daily scheduled task (default `08:00`):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_windows_task.ps1
```

Install with a custom time (24h format):

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\install_windows_task.ps1 -StartTime "09:30"
```

Run once manually through the scheduler script:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\run_bot.ps1
```

Remove the task:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\remove_windows_task.ps1
```

Notes:

- Logs are written to `logs/scheduler.log`.
- The task is registered for the current user with `Interactive` logon type and runs while you are logged in.

## Run tests

```bash
python -m unittest discover -s tests -p "test_*.py"
```

## Configuration

Required:

- `GEMINI_API_KEY`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_URN` (supports raw ID, `urn:li:person:...`, or `urn:li:member:...`)

Optional:

- `GEMINI_MODEL` (default: `gemini-2.5-flash`)
- `POST_PROMPT` (default prompt in code)
- `GEMINI_TIMEOUT_SECONDS` (default: `30`)
- `LINKEDIN_TIMEOUT_SECONDS` (default: `30`)
- `MAX_RETRIES` (default: `3`)
- `INITIAL_RETRY_DELAY_SECONDS` (default: `2`)
- `LOG_LEVEL` (default: `INFO`)

## GitHub Actions

Workflow file: `.github/workflows/daily_post.yml`

- Runs daily at `08:00 UTC`
- Supports manual trigger from the Actions tab
- Installs dependencies from `requirements.txt`
- Runs unit tests before posting

Repository secrets needed:

- `GEMINI_API_KEY`
- `LINKEDIN_ACCESS_TOKEN`
- `LINKEDIN_PERSON_URN`
