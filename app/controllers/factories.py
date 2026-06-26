"""Factory helpers for assembling application controllers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from core.models import SessionInfo
from transcription.faster_whisper_transcriber import FasterWhisperTranscriber

from app.controllers.note_controller import NoteController
from app.controllers.note_export_controller import NoteExportController
from app.controllers.transcription_controller import TranscriptionController
from app.controllers.workspace_controller import WorkspaceController


EnsureSession = Callable[[], SessionInfo]
CurrentSessionProvider = Callable[[], SessionInfo | None]


@dataclass(frozen=True, slots=True)
class Phase1Controllers:
    workspace: WorkspaceController
    transcription: TranscriptionController
    note: NoteController
    export: NoteExportController


def create_phase1_controllers(
    ensure_session: EnsureSession,
    current_session: CurrentSessionProvider,
) -> Phase1Controllers:
    def transcription_factory(**options: object) -> FasterWhisperTranscriber:
        session = current_session()
        transcript_output_path = None if session is None else session.paths["transcript.json"]
        return FasterWhisperTranscriber(
            transcript_output_path=transcript_output_path,
            **options,
        )

    return Phase1Controllers(
        workspace=WorkspaceController(),
        transcription=TranscriptionController(
            transcription_factory=transcription_factory,
            before_transcribe=ensure_session,
        ),
        note=NoteController(),
        export=NoteExportController(current_session),
    )
