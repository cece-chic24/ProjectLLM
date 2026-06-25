from pathlib import Path
from types import SimpleNamespace
import unittest

from core.errors import TranscriptionError
from core.models import TranscriptResult
from transcription.base import TranscriptionProvider
from transcription.faster_whisper_transcriber import FasterWhisperTranscriber


class FakeWhisperModel:
    created_with: dict[str, object] | None = None

    def __init__(self, model_size: str, *, device: str, compute_type: str) -> None:
        self.created_with = {
            "model_size": model_size,
            "device": device,
            "compute_type": compute_type,
        }

    def transcribe(self, audio_path: str) -> tuple[list[SimpleNamespace], SimpleNamespace]:
        segments = [
            SimpleNamespace(start=0.0, end=1.0, text=" Hello "),
            SimpleNamespace(start=1.0, end=2.5, text="world"),
        ]
        info = SimpleNamespace(language="en", language_probability=0.99)
        return segments, info


class FasterWhisperTranscriberTests(unittest.TestCase):
    def test_implements_transcription_provider_interface(self) -> None:
        transcriber = FasterWhisperTranscriber(model_factory=FakeWhisperModel)

        self.assertIsInstance(transcriber, TranscriptionProvider)

    def test_defaults_and_maps_faster_whisper_result(self) -> None:
        transcriber = FasterWhisperTranscriber(model_factory=FakeWhisperModel)

        result = transcriber.transcribe(Path("sample.wav"))

        self.assertIsInstance(result, TranscriptResult)
        self.assertEqual(result.source_path, Path("sample.wav"))
        self.assertEqual(result.text, "Hello world")
        self.assertEqual(result.language, "en")
        self.assertEqual(result.language_probability, 0.99)
        self.assertEqual(result.model_size, "base")
        self.assertEqual(result.device, "cpu")
        self.assertEqual(result.compute_type, "int8")
        self.assertEqual(result.segments[0].start, 0.0)
        self.assertEqual(result.segments[0].text, " Hello ")

    def test_rejects_cpu_float16_before_loading_model(self) -> None:
        def failing_factory(*args: object, **kwargs: object) -> FakeWhisperModel:
            raise AssertionError("model factory should not be called")

        with self.assertRaisesRegex(TranscriptionError, "float16.*cpu"):
            FasterWhisperTranscriber(compute_type="float16", model_factory=failing_factory)


if __name__ == "__main__":
    unittest.main()
