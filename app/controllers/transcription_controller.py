"""Controller for transcription workflows."""

from __future__ import annotations

from pathlib import Path

from core.errors import TranscriptionError
from core.models import TranscriptResult
from transcription.base import TranscriptionProvider


class TranscriptionController:
    """Thin orchestration layer over a transcription provider."""

    def __init__(self, transcription_provider: TranscriptionProvider) -> None:
        self._transcription_provider = transcription_provider

    def transcribe(self, audio_file_path: str | Path) -> TranscriptResult:
        try:
            return self._transcription_provider.transcribe(audio_file_path)
        except TranscriptionError:
            raise

