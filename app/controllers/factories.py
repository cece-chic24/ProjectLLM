"""Factory helpers for assembling application controllers."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

from core.models import SessionInfo
from notes.azure_openai_note_generator import AzureOpenAINoteGenerator
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse
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


class LazyAzureOpenAINoteGenerator:
    """Construct the Azure client only when the user generates a note."""

    def __init__(self) -> None:
        self._generator: AzureOpenAINoteGenerator | None = None

    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        if self._generator is None:
            self._generator = AzureOpenAINoteGenerator()
        return self._generator.generate(request)


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
        note=NoteController(LazyAzureOpenAINoteGenerator()),
        export=NoteExportController(current_session),
    )
