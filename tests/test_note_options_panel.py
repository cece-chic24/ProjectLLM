from pathlib import Path
import unittest

from PySide6.QtWidgets import QApplication

from core.models import NoteType, TranscriptResult
from ui.panels.note_options_panel import NoteOptionsPanel


class FakeNoteController:
    def __init__(self) -> None:
        self.calls = []

    def generate_note(self, transcript: TranscriptResult, note_type: NoteType):
        self.calls.append((transcript, note_type))
        return {"ok": True}


class NoteOptionsPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_generate_note_calls_controller(self) -> None:
        controller = FakeNoteController()
        panel = NoteOptionsPanel(controller)  # type: ignore[arg-type]
        transcript = TranscriptResult(
            source_path=Path("sample.wav"),
            text="Summarize this.",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )
        panel.set_transcript(transcript)
        panel._type_combo.setCurrentText("summary")

        panel._generate_note()

        self.assertEqual(controller.calls, [(transcript, NoteType.SUMMARY)])


if __name__ == "__main__":
    unittest.main()
