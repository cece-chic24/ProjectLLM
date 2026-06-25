from pathlib import Path
import unittest

from app.controllers.note_controller import NoteController
from core.errors import NoteGenerationError
from core.models import NoteType, TranscriptResult
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse


class FakeNoteGenerator:
    def __init__(self, response: NoteGenerationResponse | None = None) -> None:
        self.response = response
        self.calls: list[NoteGenerationRequest] = []

    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        self.calls.append(request)
        if self.response is None:
            raise NoteGenerationError("failed")
        return self.response


class NoteControllerTests(unittest.TestCase):
    def test_generate_note_builds_request_and_delegates_to_generator(self) -> None:
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
        response = NoteGenerationResponse(
            note_type=NoteType.SUMMARY,
            content={"summary": "Summarize this."},
            model="fake-model",
        )
        generator = FakeNoteGenerator(response)
        controller = NoteController(generator)

        actual = controller.generate_note(transcript, NoteType.SUMMARY)

        self.assertEqual(actual, response)
        self.assertEqual(
            generator.calls,
            [NoteGenerationRequest(transcript=transcript, note_type=NoteType.SUMMARY)],
        )

    def test_generate_note_propagates_typed_note_generation_errors(self) -> None:
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
        controller = NoteController(FakeNoteGenerator())

        with self.assertRaises(NoteGenerationError):
            controller.generate_note(transcript, NoteType.SUMMARY)


if __name__ == "__main__":
    unittest.main()

