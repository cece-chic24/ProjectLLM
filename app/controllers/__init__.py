"""Thin application controllers."""

from core.models import NoteType, SessionInfo, TranscriptResult, TranscriptSegment

from app.controllers.note_controller import NoteController, NoteGenerator
from app.controllers.transcription_controller import (
    TranscriptionController,
    TranscriptionFactory,
)
from app.controllers.workspace_controller import WorkspaceController

__all__ = [
    "NoteController",
    "NoteGenerator",
    "NoteType",
    "SessionInfo",
    "TranscriptResult",
    "TranscriptSegment",
    "TranscriptionController",
    "TranscriptionFactory",
    "WorkspaceController",
]
