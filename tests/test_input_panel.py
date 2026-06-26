from pathlib import Path
import unittest

from PySide6.QtWidgets import QApplication

from app.controllers import TranscriptionController
from ui.panels.input_panel import InputPanel


class FakeTranscriptionController:
    def __init__(self) -> None:
        self.calls: list[tuple[Path, str, str, str]] = []
        self.start_calls = 0
        self.stop_calls: list[tuple[str, str, str]] = []

    def transcribe(self, audio_file_path: str | Path, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        self.calls.append((Path(audio_file_path), model_size, device, compute_type))
        return {"audio": str(audio_file_path)}

    def start_recording(self) -> Path:
        self.start_calls += 1
        return Path("data/sessions/session-1/recording.wav")

    def stop_recording(self, model_size: str = "base", device: str = "cpu", compute_type: str = "int8"):
        self.stop_calls.append((model_size, device, compute_type))
        return {"audio": "data/sessions/session-1/recording.wav"}


class InputPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_transcribe_calls_controller_with_selected_options(self) -> None:
        controller = FakeTranscriptionController()
        panel = InputPanel(controller)  # type: ignore[arg-type]
        panel._audio_path_edit.setText("sample.wav")
        panel._device_combo.setCurrentText("cuda")
        panel._compute_type_combo.setCurrentText("float16")
        panel._compute_type_combo.setCurrentText("int8")

        panel._transcribe()

        self.assertEqual(controller.calls, [(Path("sample.wav"), "base", "cuda", "int8")])

    def test_invalid_combo_blocks_controller_call(self) -> None:
        controller = FakeTranscriptionController()
        panel = InputPanel(controller)  # type: ignore[arg-type]
        panel._audio_path_edit.setText("sample.wav")
        panel._device_combo.setCurrentText("cpu")
        panel._compute_type_combo.setCurrentText("float16")

        panel._transcribe()

        self.assertEqual(controller.calls, [])

    def test_record_button_starts_and_stops_recording_through_controller(self) -> None:
        controller = FakeTranscriptionController()
        panel = InputPanel(controller)  # type: ignore[arg-type]
        transcripts = []
        panel.transcript_ready.connect(transcripts.append)
        panel._device_combo.setCurrentText("cuda")
        panel._compute_type_combo.setCurrentText("int8")

        panel._record_button.click()
        panel._record_button.click()

        self.assertEqual(controller.start_calls, 1)
        self.assertEqual(controller.stop_calls, [("base", "cuda", "int8")])
        self.assertEqual(panel._audio_path_edit.text(), "data\\sessions\\session-1\\recording.wav")
        self.assertEqual(transcripts, [{"audio": "data/sessions/session-1/recording.wav"}])


if __name__ == "__main__":
    unittest.main()
