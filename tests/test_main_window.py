from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PySide6.QtWidgets import QApplication

from app.controllers import NoteType, SessionInfo, TranscriptResult
from notes.note_types import NoteGenerationResponse
from ui.main_window import MainWindow


class FakeWorkspaceController:
    def __init__(self) -> None:
        self.session = SessionInfo(
            session_id="session-1",
            created_at=datetime(2026, 6, 25, 12, 0, 0),
            paths={
                "session_dir": Path("sessions/session-1"),
                "note.json": Path("sessions/session-1/note.json"),
                "note.md": Path("sessions/session-1/note.md"),
                "note.txt": Path("sessions/session-1/note.txt"),
            },
        )
        self.create_calls = 0

    def create_session(self) -> SessionInfo:
        self.create_calls += 1
        return self.session


class FakeTranscriptionController:
    def transcribe(self, audio_file_path: str | Path, **options: object) -> TranscriptResult:
        return TranscriptResult(
            source_path=Path(audio_file_path),
            text="Hello",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )


class FakeNoteController:
    def generate_note(self, transcript: TranscriptResult, note_type: NoteType) -> NoteGenerationResponse:
        return NoteGenerationResponse(note_type, {"summary": transcript.text}, "fake-model")


class FakeExportController:
    def export_note(self, note: object) -> dict[str, Path]:
        return {}


class FakeCleanupDialog:
    created_with: tuple[object, SessionInfo, object] | None = None

    def __init__(self, workspace_controller: object, session: SessionInfo, parent: object) -> None:
        self.__class__.created_with = (workspace_controller, session, parent)

    def exec(self) -> int:
        return 1


class MainWindowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_window_wires_phase1_panels_and_session_cleanup(self) -> None:
        workspace = FakeWorkspaceController()
        controllers = SimpleNamespace(
            workspace=workspace,
            transcription=FakeTranscriptionController(),
            note=FakeNoteController(),
            export=FakeExportController(),
        )
        window = MainWindow(controllers)  # type: ignore[arg-type]
        transcript = controllers.transcription.transcribe(Path("input.wav"))
        note = controllers.note.generate_note(transcript, NoteType.SUMMARY)

        session = window._ensure_session()
        window._handle_transcript_ready(transcript)
        window._handle_note_ready(note)

        self.assertEqual(session.session_id, "session-1")
        self.assertEqual(workspace.create_calls, 1)
        self.assertTrue(window._delete_button.isEnabled())
        self.assertTrue(window._note_options_panel._generate_button.isEnabled())
        self.assertTrue(window._note_view_panel._export_button.isEnabled())

        with patch("ui.main_window.SessionCleanupDialog", FakeCleanupDialog):
            window._confirm_delete_session()

        self.assertEqual(FakeCleanupDialog.created_with, (workspace, session, window))
        self.assertFalse(window._delete_button.isEnabled())
        self.assertIsNone(window._get_current_session())

    def test_window_routes_note_generation_failure_to_note_view(self) -> None:
        workspace = FakeWorkspaceController()
        controllers = SimpleNamespace(
            workspace=workspace,
            transcription=FakeTranscriptionController(),
            note=FakeNoteController(),
            export=FakeExportController(),
        )
        window = MainWindow(controllers)  # type: ignore[arg-type]

        window._handle_note_failed("Note generation is not configured.")

        self.assertEqual(window._note_view_panel._meta_label.text(), "Note generation failed.")
        self.assertEqual(window._note_view_panel._text_edit.toPlainText(), "Note generation is not configured.")
        self.assertFalse(window._note_view_panel._export_button.isEnabled())


if __name__ == "__main__":
    unittest.main()
