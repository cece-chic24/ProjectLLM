from pathlib import Path
from types import SimpleNamespace
import tempfile
import unittest

from core.models import TranscriptResult, TranscriptSegment
from transcription.faster_whisper_transcriber import FasterWhisperTranscriber
from transcription.transcript_store import load_transcript, save_transcript


class FakeWhisperModel:
    def __init__(self, model_size: str, *, device: str, compute_type: str) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type

    def transcribe(self, audio_path: str) -> tuple[list[SimpleNamespace], SimpleNamespace]:
        segments = [
            SimpleNamespace(start=0.0, end=1.5, text="First segment."),
            SimpleNamespace(start=1.5, end=3.0, text="Second segment."),
        ]
        info = SimpleNamespace(language="en", language_probability=0.97)
        return segments, info


class TranscriptStoreTests(unittest.TestCase):
    def test_transcript_result_round_trips_through_json_with_all_fields(self) -> None:
        result = TranscriptResult(
            source_path=Path("input.wav"),
            text="First segment. Second segment.",
            language="en",
            language_probability=0.97,
            segments=[
                TranscriptSegment(start=0.0, end=1.5, text="First segment."),
                TranscriptSegment(start=1.5, end=3.0, text="Second segment."),
            ],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transcript.json"
            save_transcript(result, path)

            loaded = load_transcript(path)

        self.assertEqual(loaded, result)

    def test_transcriber_saves_transcript_immediately_when_output_path_is_configured(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            transcript_path = Path(directory) / "transcript.json"
            transcriber = FasterWhisperTranscriber(
                model_factory=FakeWhisperModel,
                transcript_output_path=transcript_path,
            )

            result = transcriber.transcribe(Path("input.wav"))

            self.assertTrue(transcript_path.exists())
            self.assertEqual(load_transcript(transcript_path), result)


if __name__ == "__main__":
    unittest.main()

