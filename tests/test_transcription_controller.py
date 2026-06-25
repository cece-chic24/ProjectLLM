from pathlib import Path
import unittest

from app.controllers.transcription_controller import TranscriptionController
from core.errors import TranscriptionError
from core.models import TranscriptResult
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


if __name__ == "__main__":
    unittest.main()

