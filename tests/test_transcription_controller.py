from pathlib import Path
import unittest
from datetime import datetime

from app.controllers.transcription_controller import TranscriptionController
from core.errors import TranscriptionError
from core.models import SessionInfo, TranscriptResult
from transcription.base import TranscriptionProvider


class FakeTranscriptionProvider(TranscriptionProvider):
    def __init__(self, result: TranscriptResult | None = None) -> None:
        self.result = result
        self.calls: list[Path] = []

    def transcribe(self, audio_file_path: str | Path) -> TranscriptResult:
        self.calls.append(Path(audio_file_path))
        if self.result is None:
            raise TranscriptionError("failed")
        return self.result


class FakeAudioRecorder:
    instances: list["FakeAudioRecorder"] = []

    def __init__(self, output_path: Path, *, device: int | str | None = None) -> None:
        self.output_path = output_path
        self.device = device
        self.started = False
        self.stopped = False
        self.__class__.instances.append(self)

    def start(self) -> None:
        self.started = True

    def stop(self) -> None:
        self.stopped = True


class TranscriptionControllerTests(unittest.TestCase):
    def test_transcribe_delegates_to_provider(self) -> None:
        result = TranscriptResult(
            source_path=Path("sample.wav"),
            text="Hello",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )
        provider = FakeTranscriptionProvider(result)
        controller = TranscriptionController(provider)

        actual = controller.transcribe(Path("sample.wav"))

        self.assertEqual(actual, result)
        self.assertEqual(provider.calls, [Path("sample.wav")])

    def test_transcribe_propagates_typed_transcription_errors(self) -> None:
        controller = TranscriptionController(FakeTranscriptionProvider())

        with self.assertRaises(TranscriptionError):
            controller.transcribe(Path("broken.wav"))

    def test_recording_starts_in_session_folder_and_stop_transcribes_recording(self) -> None:
        result = TranscriptResult(
            source_path=Path("sessions/session-1/recording.wav"),
            text="Hello",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="small",
            device="cpu",
            compute_type="int8",
        )
        provider = FakeTranscriptionProvider(result)
        session = SessionInfo(
            session_id="session-1",
            created_at=datetime(2026, 6, 26, 12, 0, 0),
            paths={"session_dir": Path("sessions/session-1")},
        )
        FakeAudioRecorder.instances = []
        controller = TranscriptionController(
            provider,
            before_transcribe=lambda: session,
            audio_recorder_factory=FakeAudioRecorder,
        )

        recording_path = controller.start_recording()
        actual = controller.stop_recording(model_size="small", device="cpu", compute_type="int8")

        self.assertEqual(recording_path, Path("sessions/session-1/recording.wav"))
        self.assertTrue(FakeAudioRecorder.instances[0].started)
        self.assertTrue(FakeAudioRecorder.instances[0].stopped)
        self.assertEqual(provider.calls, [Path("sessions/session-1/recording.wav")])
        self.assertEqual(actual, result)

    def test_recording_device_override_is_passed_to_audio_recorder(self) -> None:
        result = TranscriptResult(
            source_path=Path("sessions/session-1/recording.wav"),
            text="Hello",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="small",
            device="cpu",
            compute_type="int8",
        )
        provider = FakeTranscriptionProvider(result)
        session = SessionInfo(
            session_id="session-1",
            created_at=datetime(2026, 6, 26, 12, 0, 0),
            paths={"session_dir": Path("sessions/session-1")},
        )
        FakeAudioRecorder.instances = []
        controller = TranscriptionController(
            provider,
            before_transcribe=lambda: session,
            audio_recorder_factory=FakeAudioRecorder,
        )

        controller.start_recording(device=9)

        self.assertEqual(FakeAudioRecorder.instances[0].device, 9)


if __name__ == "__main__":
    unittest.main()
