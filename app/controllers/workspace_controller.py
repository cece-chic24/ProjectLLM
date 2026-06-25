"""Controller for workspace session lifecycle operations."""

from __future__ import annotations

from collections.abc import Callable
from datetime import datetime
from pathlib import Path

from core.errors import FileDeletionError
from core.models import SessionInfo
from storage.session_store import create_session_folder, delete_session_folder


CreateSession = Callable[[str | Path, datetime | None], SessionInfo]
DeleteSession = Callable[[str | Path], None]


class WorkspaceController:
    """Thin orchestration layer over session storage."""

    def __init__(
        self,
        create_session: CreateSession = create_session_folder,
        delete_session: DeleteSession = delete_session_folder,
    ) -> None:
        self._create_session = create_session
        self._delete_session = delete_session

    def create_session(
        self,
        base_dir: str | Path = Path("data") / "sessions",
        created_at: datetime | None = None,
    ) -> SessionInfo:
        return self._create_session(base_dir, created_at)

    def delete_session(self, session_dir: str | Path) -> None:
        try:
            self._delete_session(session_dir)
        except FileDeletionError:
            raise

