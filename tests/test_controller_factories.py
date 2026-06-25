from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from app.controllers import NoteType, SessionInfo, TranscriptResult, create_phase1_controllers
from notes.note_types import NoteGenerationResponse


class FakeTranscriber:
    calls: list[dict[str, object]] = []

    def __init__(self, **options: object) -> None:
        self.calls.append(options)

    def transcribe(self, audio_file_path: str | Path) -> TranscriptResult:
        return TranscriptResult(
            source_path=Path(audio_file_path),
            text="Hello",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size=str(self.calls[-1]["model_size"]),
            device=str(self.calls[-1]["device"]),
            compute_type=str(self.calls[-1]["compute_type"]),
        )


class FakeAzureGenerator:
    created = 0

    def __init__(self) -> None:
        self.__class__.created += 1

    def generate(self, request: object) -> NoteGenerationResponse:
        note_type = getattr(request, "note_type")
        return NoteGenerationResponse(
            note_type=note_type,
            content={"summary": "Hello"},
            model="fake-model",
        )


class ControllerFactoryTests(unittest.TestCase):
    def setUp(self) -> None:
        FakeTranscriber.calls = []
        FakeAzureGenerator.created = 0

    def test_create_phase1_controllers_wires_session_aware_services(self) -> None:
        session = SessionInfo(
            session_id="session-1",
            created_at=datetime(2026, 6, 25, 12, 0, 0),
            paths={
                "transcript.json": Path("sessions/session-1/transcript.json"),
                "note.json": Path("sessions/session-1/note.json"),
                "note.md": Path("sessions/session-1/note.md"),
                "note.txt": Path("sessions/session-1/note.txt"),
            },
        )
        ensure_calls: list[None] = []

        def ensure_session() -> SessionInfo:
            ensure_calls.append(None)
            return session

        with (
            patch("app.controllers.factories.FasterWhisperTranscriber", FakeTranscriber),
            patch("app.controllers.factories.AzureOpenAINoteGenerator", FakeAzureGenerator),
        ):
            controllers = create_phase1_controllers(ensure_session, lambda: session)

            transcript = controllers.transcription.transcribe(
                Path("input.wav"),
                model_size="small",
                device="cpu",
                compute_type="int8",
            )
            response = controllers.note.generate_note(transcript, NoteType.SUMMARY)

        self.assertEqual(len(ensure_calls), 1)
        self.assertEqual(
            FakeTranscriber.calls,
            [
                {
                    "transcript_output_path": Path("sessions/session-1/transcript.json"),
                    "model_size": "small",
                    "device": "cpu",
                    "compute_type": "int8",
                }
            ],
        )
        self.assertEqual(FakeAzureGenerator.created, 1)
        self.assertEqual(response, NoteGenerationResponse(NoteType.SUMMARY, {"summary": "Hello"}, "fake-model"))

    def test_note_generator_is_lazy(self) -> None:
        with patch("app.controllers.factories.AzureOpenAINoteGenerator", FakeAzureGenerator):
            controllers = create_phase1_controllers(
                lambda: SimpleNamespace(),
                lambda: None,
            )

        self.assertEqual(FakeAzureGenerator.created, 0)
        self.assertIsNotNone(controllers.note)


if __name__ == "__main__":
    unittest.main()
