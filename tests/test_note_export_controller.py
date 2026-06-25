from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import json
import tempfile
import unittest

from app.controllers import NoteExportController, SessionInfo
from core.errors import ExportError


class NoteExportControllerTests(unittest.TestCase):
    def test_export_note_writes_all_session_note_files(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            session_dir = Path(directory)
            session = SessionInfo(
                session_id="session-1",
                created_at=datetime(2026, 6, 25, 12, 0, 0),
                paths={
                    "note.json": session_dir / "note.json",
                    "note.md": session_dir / "note.md",
                    "note.txt": session_dir / "note.txt",
                },
            )
            note = SimpleNamespace(
                note_type="summary",
                model="fake-model",
                content={"summary": "Hello"},
            )
            controller = NoteExportController(lambda: session)

            paths = controller.export_note(note)

            self.assertEqual(paths["json"], session_dir / "note.json")
            self.assertEqual(json.loads(paths["json"].read_text(encoding="utf-8"))["content"], {"summary": "Hello"})
            self.assertIn("# Summary", paths["markdown"].read_text(encoding="utf-8"))
            self.assertIn("Summary:", paths["text"].read_text(encoding="utf-8"))

    def test_export_note_requires_active_session(self) -> None:
        controller = NoteExportController(lambda: None)

        with self.assertRaises(ExportError):
            controller.export_note(SimpleNamespace())


if __name__ == "__main__":
    unittest.main()
