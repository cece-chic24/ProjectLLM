from pathlib import Path
import unittest

from core.models import NoteType, TranscriptResult
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse


class NoteTypesTests(unittest.TestCase):
    def test_request_and_response_are_tied_to_note_type(self) -> None:
        transcript = TranscriptResult(
            source_path=Path("lecture.wav"),
            text="The instructor reviewed recursive functions.",
            language="en",
            language_probability=0.95,
            segments=[],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )

        request = NoteGenerationRequest(
            transcript=transcript,
            note_type=NoteType.LECTURE,
        )
        response = NoteGenerationResponse(
            note_type=NoteType.LECTURE,
            content={"summary": "The instructor reviewed recursive functions."},
            model="deployment-name",
        )

        self.assertEqual(request.note_type, NoteType.LECTURE)
        self.assertEqual(request.transcript, transcript)
        self.assertEqual(response.note_type, request.note_type)
        self.assertEqual(
            response.content,
            {"summary": "The instructor reviewed recursive functions."},
        )


if __name__ == "__main__":
    unittest.main()
