"""Per-session folder management."""
from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path

from core.errors import FileDeletionError
from core.models import SessionInfo


SESSION_FILENAMES = (
    "source_info.json",
    "transcript.json",
    "transcript.txt",
    "note.json",
    "note.md",
    "note.txt",
    "session.log",
)


def create_session_folder(
    base_dir: str | Path = Path("data") / "sessions",
    created_at: datetime | None = None,
) -> SessionInfo:
    """Create a timestamped session folder with the expected file layout."""
    resolved_created_at = created_at or datetime.now()
    timestamp = resolved_created_at.strftime("%Y-%m-%d_%H%M%S")
    session_dir = _unique_session_dir(Path(base_dir), timestamp)
    session_dir.mkdir(parents=True, exist_ok=False)

    paths: dict[str, Path] = {}
    for filename in SESSION_FILENAMES:
        path = session_dir / filename
        path.touch()
        paths[filename] = path

    paths["session_dir"] = session_dir
    _write_source_info(paths["source_info.json"], session_id=session_dir.name)
    return SessionInfo(
        session_id=session_dir.name,
        created_at=resolved_created_at,
        paths=paths,
    )


def delete_session_folder(session_dir: str | Path) -> None:
    """Delete a session folder and all files below it."""
    path = Path(session_dir)
    try:
        shutil.rmtree(path)
    except OSError as exc:
        raise FileDeletionError(
            f"Could not delete session folder {path}: {exc}"
        ) from exc


def load_session_folder(session_dir: str | Path) -> SessionInfo:
    """Reconstruct a SessionInfo from an existing folder on disk."""
    folder = Path(session_dir)
    if not folder.is_dir():
        raise FileNotFoundError(f"Session folder not found: {folder}")

    paths: dict[str, Path] = {"session_dir": folder}
    for filename in SESSION_FILENAMES:
        p = folder / filename
        paths[filename] = p  # include whether it exists or not

    # Parse creation time from folder name (format: YYYY-MM-DD_HHMMSS)
    try:
        created_at = datetime.strptime(folder.name[:17], "%Y-%m-%d_%H%M%S")
    except ValueError:
        created_at = datetime.fromtimestamp(folder.stat().st_ctime)

    return SessionInfo(
        session_id=folder.name,
        created_at=created_at,
        paths=paths,
    )


def _unique_session_dir(base_dir: Path, timestamp: str) -> Path:
    candidate = base_dir / timestamp
    if not candidate.exists():
        return candidate
    suffix = 2
    while True:
        candidate = base_dir / f"{timestamp}_{suffix}"
        if not candidate.exists():
            return candidate
        suffix += 1


def _write_source_info(path: Path, session_id: str) -> None:
    path.write_text(
        json.dumps({"session_id": session_id}, indent=2), encoding="utf-8"
    )