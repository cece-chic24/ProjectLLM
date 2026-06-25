"""Transcription provider interface."""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path

from core.models import TranscriptResult


class TranscriptionProvider(ABC):
    """Interface for audio transcription providers."""

    @abstractmethod
    def transcribe(self, audio_file_path: str | Path) -> TranscriptResult:
        """Transcribe an audio file into structured transcript data."""

