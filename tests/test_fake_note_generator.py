from pathlib import Path
import unittest

from core.models import NoteType, TranscriptResult, TranscriptSegment
from notes.fake_note_generator import FakeNoteGenerator
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse


class FakeNoteGeneratorTests(unittest.TestCase):
    def test_generate_returns_deterministic_sample_note(self) -> None:
        transcript = TranscriptResult(
            source_path=Path("meeting.wav"),
            text="Discuss roadmap and release tasks.",
            language="en",
            language_probability=0.98,
            segments=[
                TranscriptSegment(start=0.0, end=1.0, text="Discuss roadmap."),
                TranscriptSegment(start=1.0, end=2.0, text="Release tasks."),
            ],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )
        request = NoteGenerationRequest(transcript=transcript, note_type=NoteType.SUMMARY)

        response = FakeNoteGenerator().generate(request)

        self.assertEqual(
            response,
            NoteGenerationResponse(
                note_type=NoteType.SUMMARY,
                content={
                    "summary": "Sample summary note for meeting.wav.",
                    "key_points": [
                        "This note was generated locally for UI testing.",
                        "Transcript language: en",
                        "Transcript segments: 2",
                    ],
                    "action_items": [
                        "Verify the transcript content.",
                        "Export the generated note files.",
                        "Delete the session when finished testing.",
                    ],
                    "transcript_preview": "Discuss roadmap and release tasks.",
                },
                model="fake-note-generator",
            ),
        )


if __name__ == "__main__":
    unittest.main()
