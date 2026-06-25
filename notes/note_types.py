"""Typed request and response shapes for note generation."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from core.models import NoteType, TranscriptResult


@dataclass(frozen=True, slots=True)
class NoteGenerationRequest:
    transcript: TranscriptResult
    note_type: NoteType


@dataclass(frozen=True, slots=True)
class NoteGenerationResponse:
    note_type: NoteType
    content: dict[str, Any]
    model: str

