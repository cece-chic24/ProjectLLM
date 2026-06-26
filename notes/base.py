"""Shared note generator interface."""

from __future__ import annotations

from abc import ABC, abstractmethod

from notes.note_types import NoteGenerationRequest, NoteGenerationResponse


class NoteGenerator(ABC):
    """Interface implemented by note generation providers."""

    @abstractmethod
    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        """Generate structured notes for a transcript request."""
