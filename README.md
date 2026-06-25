# ProjectLLM

ProjectLLM is a greenfield Python 3.13 rebuild of a desktop app for transcribing audio and generating AI notes. Phase 0 is repository bootstrap only; feature code starts after Phase 0 is approved.

## Setup

Create and activate a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install the project with development tools:

```powershell
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Create a local environment file from the placeholder template:

```powershell
Copy-Item .env.example .env
```

Put real Azure OpenAI values only in `.env`. Do not commit `.env`.

## Checks

Run the unit tests:

```powershell
python -m pytest
```

Run the secret check against all files:

```powershell
python scripts/check_secrets.py --all
```

To enable the tracked pre-commit hook:

```powershell
git config core.hooksPath .githooks
```

The hook scans staged files and fails the commit if it finds real-looking API keys.
