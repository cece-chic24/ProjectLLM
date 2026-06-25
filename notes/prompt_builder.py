"""Build source-faithful prompts for AI note generation.

The generated prompt must instruct the model to never invent owners, dates,
or decisions not present in the source transcript and to stay strictly
source-faithful.
"""

from __future__ import annotations

from core.models import NoteType, TranscriptResult


SOURCE_FAITHFULNESS_RULE = (
    "Never invent owners, dates, or decisions not present in the source "
    "transcript. Stay strictly source-faithful."
)


def build_note_prompt(transcript: TranscriptResult, note_type: NoteType) -> str:
    """Build a prompt that requires strictly source-faithful note generation.

    The prompt explicitly forbids inventing owners, dates, or decisions not
    present in the source transcript.
    """
    segments = "\n".join(
        f"[{segment.start:.2f}-{segment.end:.2f}] {segment.text.strip()}"
        for segment in transcript.segments
        if segment.text.strip()
    )

    return "\n".join(
        [
            "Generate structured JSON notes from the source transcript.",
            f"Note type: {note_type.value}",
            f"Source file: {transcript.source_path}",
            f"Language: {transcript.language}",
            "",
            "Rules:",
            f"- {SOURCE_FAITHFULNESS_RULE}",
            "- If a requested field is not supported by the transcript, use null or an empty list.",
            "- Return JSON only, with no Markdown fences or commentary.",
            "",
            "Transcript text:",
            transcript.text.strip(),
            "",
            "Timestamped segments:",
            segments,
        ]
    )

