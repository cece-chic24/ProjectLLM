"""Run ProjectLLM as a module."""

from __future__ import annotations

from core.environment import load_project_dotenv

load_project_dotenv()

from main import main


if __name__ == "__main__":
    raise SystemExit(main())
