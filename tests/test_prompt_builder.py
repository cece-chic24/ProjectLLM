from pathlib import Path
import unittest

from core.models import NoteType, TranscriptResult, TranscriptSegment
from notes.prompt_builder import SOURCE_FAITHFULNESS_RULE, build_note_prompt


class PromptBuilderTests(unittest.TestCase):
    def test_prompt_includes_note_type_transcript_and_source_faithfulness_rule(self) -> None:
        transcript = TranscriptResult(
            source_path=Path("meeting.wav"),
            text="Alex said the launch decision is postponed. Priya owns the follow-up.",
            language="en",
            language_probability=0.98,
            segments=[
                TranscriptSegment(
                    start=0.0,
                    end=3.5,
                    text="Alex said the launch decision is postponed.",
                ),
                TranscriptSegment(
                    start=3.5,
                    end=6.0,
                    text="Priya owns the follow-up.",
                ),
            ],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )

        prompt = build_note_prompt(transcript, NoteType.MEETING)

        self.assertIn("Note type: meeting", prompt)
        self.assertIn("meeting.wav", prompt)
        self.assertIn("Alex said the launch decision is postponed.", prompt)
        self.assertIn("[3.50-6.00] Priya owns the follow-up.", prompt)
        self.assertIn(SOURCE_FAITHFULNESS_RULE, prompt)
        self.assertIn("Return JSON only", prompt)


if __name__ == "__main__":
    unittest.main()

