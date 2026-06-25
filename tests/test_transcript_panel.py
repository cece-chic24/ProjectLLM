from types import SimpleNamespace
import unittest

from PySide6.QtWidgets import QApplication

from ui.panels.transcript_panel import TranscriptPanel


class FakeTranscriptionController:
    def __init__(self) -> None:
        self.calls = []
        self.transcript = SimpleNamespace(
            segments=[
                SimpleNamespace(start=0.0, end=1.25, text="Hello"),
                SimpleNamespace(start=1.25, end=2.5, text="World"),
            ]
        )

    def transcribe(self, audio_file_path, model_size="base", device="cpu", compute_type="int8"):
        self.calls.append((audio_file_path, model_size, device, compute_type))
        return self.transcript


class TranscriptPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_load_transcript_calls_controller_and_displays_segments(self) -> None:
        controller = FakeTranscriptionController()
        panel = TranscriptPanel(controller)

        panel.load_transcript("sample.wav")

        self.assertEqual(controller.calls, [("sample.wav", "base", "cpu", "int8")])
        self.assertEqual(panel._table.rowCount(), 2)
        self.assertEqual(panel._table.item(0, 2).text(), "Hello")
        self.assertEqual(panel._table.item(1, 2).text(), "World")


if __name__ == "__main__":
    unittest.main()
