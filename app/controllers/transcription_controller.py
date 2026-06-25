"""Controller for transcription workflows."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from core.errors import TranscriptionError
from core.models import TranscriptResult
from transcription.base import TranscriptionProvider


TranscriptionFactory = Callable[..., TranscriptionProvider]
BeforeTranscribe = Callable[[], None]


class TranscriptionController:
    """Thin orchestration layer over a transcription provider."""

    def __init__(
        self,
        transcription_provider: TranscriptionProvider | None = None,
        transcription_factory: TranscriptionFactory | None = None,
        before_transcribe: BeforeTranscribe | None = None,
    ) -> None:
        self._transcription_provider = transcription_provider
        self._transcription_factory = transcription_factory
        self._before_transcribe = before_transcribe

    def transcribe(
        self,
        audio_file_path: str | Path,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> TranscriptResult:
        try:
            if self._before_transcribe is not None:
                self._before_transcribe()
            provider = self._resolve_provider(model_size, device, compute_type)
            return provider.transcribe(audio_file_path)
        except TranscriptionError:
            raise

    def _resolve_provider(
        self,
        model_size: str,
        device: str,
        compute_type: str,
    ) -> TranscriptionProvider:
        if self._transcription_factory is not None:
            return self._transcription_factory(
                model_size=model_size,
                device=device,
                compute_type=compute_type,
            )
        if self._transcription_provider is None:
            raise TranscriptionError("No transcription provider is configured.")
        return self._transcription_provider
