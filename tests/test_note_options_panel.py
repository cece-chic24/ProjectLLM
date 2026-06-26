from pathlib import Path
import unittest

from PySide6.QtWidgets import QApplication

from app.controllers import NoteGenerationError
from core.models import NoteType, TranscriptResult
from ui.panels.note_options_panel import NoteOptionsPanel


class FakeNoteController:
    def __init__(self) -> None:
        self.calls = []

    def generate_note(self, transcript: TranscriptResult, note_type: NoteType):
        self.calls.append((transcript, note_type))
        return {"ok": True}


class FailingNoteController:
    def generate_note(self, transcript: TranscriptResult, note_type: NoteType):
        raise NoteGenerationError("Note generation is not configured.")


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
        self.assertIs(type(controller.calls[0][1]), NoteType)

    def test_generate_note_displays_and_emits_generation_failure(self) -> None:
        panel = NoteOptionsPanel(FailingNoteController())  # type: ignore[arg-type]
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
        messages: list[str] = []
        panel.note_failed.connect(messages.append)
        panel.set_transcript(transcript)

        panel._generate_note()

        self.assertEqual(messages, ["Note generation is not configured."])
        self.assertEqual(panel._status_label.text(), "Note generation is not configured.")


if __name__ == "__main__":
    unittest.main()
