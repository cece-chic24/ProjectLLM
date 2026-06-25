"""Pre-commit secret scanner for ProjectLLM."""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", ".venv", "__pycache__", "data", "dist", "build", ".pytest_cache", ".mypy_cache", ".ruff_cache"}
SKIP_SUFFIXES = {".pyc", ".pyo"}
PLACEHOLDER_MARKERS = ("placeholder", "your-", "example", "changeme", "dummy", "fake")

PATTERNS = (
    re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b"),
    re.compile(
        r"(?i)\b(?:azure_openai_api_key|openai_api_key|api_key)\b\s*[:=]\s*['\"]?([A-Za-z0-9_\-]{20,})['\"]?"
    ),
)


def is_placeholder(value: str) -> bool:
    lowered = value.lower()
    return any(marker in lowered for marker in PLACEHOLDER_MARKERS)


def find_secret_lines(text: str) -> list[tuple[int, str]]:
    findings: list[tuple[int, str]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        for pattern in PATTERNS:
            match = pattern.search(line)
            if not match:
                continue
            value = match.group(1) if match.groups() else match.group(0)
            if not is_placeholder(value):
                findings.append((line_number, line.strip()))
                break
    return findings


def should_scan(path: Path) -> bool:
    if any(part in SKIP_DIRS for part in path.parts):
        return False
    return path.suffix not in SKIP_SUFFIXES


def staged_files() -> list[Path]:
    result = subprocess.run(
        ["git", "diff", "--cached", "--name-only", "--diff-filter=ACMR"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    )
    return [ROOT / line for line in result.stdout.splitlines() if line.strip()]


def all_files() -> list[Path]:
    return [path for path in ROOT.rglob("*") if path.is_file()]


def scan_files(paths: list[Path]) -> list[str]:
    messages: list[str] = []
    for path in paths:
        if not should_scan(path):
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in find_secret_lines(text):
            relative = path.relative_to(ROOT)
            messages.append(f"{relative}:{line_number}: real-looking API key: {line}")
    return messages


def main() -> int:
    parser = argparse.ArgumentParser(description="Block commits containing real-looking API keys.")
    parser.add_argument("--all", action="store_true", help="Scan all repository files instead of staged files.")
    args = parser.parse_args()

    paths = all_files() if args.all else staged_files()
    findings = scan_files(paths)
    if findings:
        print("Secret check failed. Remove real API keys before committing.", file=sys.stderr)
        for finding in findings:
            print(finding, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

