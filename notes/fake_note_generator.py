"""Deterministic note generator for local UI testing."""

from __future__ import annotations

from notes.base import NoteGenerator
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse


class FakeNoteGenerator(NoteGenerator):
    """Generate a stable sample note without external services."""

    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        transcript = request.transcript
        source_name = transcript.source_path.name
        preview = transcript.text.strip() or "No transcript text was available."

        return NoteGenerationResponse(
            note_type=request.note_type,
            content={
                "summary": f"Sample {request.note_type.value} note for {source_name}.",
                "key_points": [
                    "This note was generated locally for UI testing.",
                    f"Transcript language: {transcript.language}",
                    f"Transcript segments: {len(transcript.segments)}",
                ],
                "action_items": [
                    "Verify the transcript content.",
                    "Export the generated note files.",
                    "Delete the session when finished testing.",
                ],
                "transcript_preview": preview[:240],
            },
            model="fake-note-generator",
        )
