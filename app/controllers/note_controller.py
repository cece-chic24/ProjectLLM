"""Controller for note generation workflows."""

from __future__ import annotations

from typing import Protocol

from core.errors import AzureOpenAIConfigurationError, NoteGenerationError
from core.models import NoteType, TranscriptResult
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse


class NoteGenerator(Protocol):
    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        """Generate notes for a structured note request."""


class NoteController:
    """Thin orchestration layer over a note generator."""

    def __init__(self, note_generator: NoteGenerator) -> None:
        self._note_generator = note_generator

    def generate_note(
        self,
        transcript: TranscriptResult,
        note_type: NoteType,
    ) -> NoteGenerationResponse:
        request = NoteGenerationRequest(transcript=transcript, note_type=note_type)
        try:
            return self._note_generator.generate(request)
        except (AzureOpenAIConfigurationError, NoteGenerationError):
            raise

