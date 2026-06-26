"""Environment loading helpers."""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def load_project_dotenv(dotenv_path: Path | None = None) -> bool:
    """Load the project .env file without depending on the launch directory."""
    path = dotenv_path if dotenv_path is not None else PROJECT_ROOT / ".env"
    return load_dotenv(path)
