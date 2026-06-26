"""Thin application controllers."""

from core.errors import GeminiConfigurationError, NoteGenerationError
from core.models import NoteType, SessionInfo, TranscriptResult, TranscriptSegment

from app.controllers.factories import Phase1Controllers, create_phase1_controllers
from app.controllers.note_controller import (
    NOTE_PROVIDER_ENV_VAR,
    NoteController,
    create_note_generator_from_config,
)
from app.controllers.note_export_controller import NoteExportController
from notes.base import NoteGenerator
from app.controllers.transcription_controller import (
    TranscriptionController,
    TranscriptionFactory,
)
from app.controllers.workspace_controller import WorkspaceController

__all__ = [
    "GeminiConfigurationError",
    "NoteController",
    "NoteExportController",
    "NoteGenerator",
    "NoteGenerationError",
    "NoteType",
    "NOTE_PROVIDER_ENV_VAR",
    "Phase1Controllers",
    "SessionInfo",
    "TranscriptResult",
    "TranscriptSegment",
    "TranscriptionController",
    "TranscriptionFactory",
    "WorkspaceController",
    "create_note_generator_from_config",
    "create_phase1_controllers",
]
