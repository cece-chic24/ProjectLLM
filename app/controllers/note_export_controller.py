"""Controller for exporting generated notes into the current session."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from core.errors import ExportError
from core.models import SessionInfo
from notes.exporters import export_note_json, export_note_markdown, export_note_text


CurrentSessionProvider = Callable[[], SessionInfo | None]


class NoteExportController:
    """Write generated note files to the active session folder."""

    def __init__(self, current_session: CurrentSessionProvider) -> None:
        self._current_session = current_session

    def export_note(self, note: object) -> dict[str, Path]:
        session = self._current_session()
        if session is None:
            raise ExportError("No active session is available for note export.")

        paths = {
            "json": export_note_json(note, session.paths["note.json"]),
            "markdown": export_note_markdown(note, session.paths["note.md"]),
            "text": export_note_text(note, session.paths["note.txt"]),
        }
        return paths
