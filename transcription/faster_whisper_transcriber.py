"""faster-whisper transcription provider."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

from core.errors import TranscriptionError
from core.models import TranscriptResult, TranscriptSegment
from transcription.base import TranscriptionProvider


ModelFactory = Callable[..., Any]


class FasterWhisperTranscriber(TranscriptionProvider):
    """Transcribe audio using faster-whisper."""

    def __init__(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
        model_factory: ModelFactory | None = None,
    ) -> None:
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self._model_factory = model_factory
        self._model: Any | None = None
        self._validate_runtime_options()

    def transcribe(self, audio_file_path: str | Path) -> TranscriptResult:
        self._validate_runtime_options()
        source_path = Path(audio_file_path)

        try:
            raw_segments, info = self._load_model().transcribe(str(source_path))
            segments = [
                TranscriptSegment(start=segment.start, end=segment.end, text=segment.text)
                for segment in raw_segments
            ]
        except TranscriptionError:
            raise
        except Exception as exc:
            raise TranscriptionError(f"faster-whisper transcription failed: {exc}") from exc

        return TranscriptResult(
            source_path=source_path,
            text=" ".join(segment.text.strip() for segment in segments if segment.text.strip()),
            language=info.language,
            language_probability=info.language_probability,
            segments=segments,
            model_size=self.model_size,
            device=self.device,
            compute_type=self.compute_type,
        )

    def _load_model(self) -> Any:
        if self._model is None:
            factory = self._model_factory or self._default_model_factory()
            self._model = factory(
                self.model_size,
                device=self.device,
                compute_type=self.compute_type,
            )
        return self._model

    def _default_model_factory(self) -> ModelFactory:
        try:
            from faster_whisper import WhisperModel
        except ImportError as exc:
            raise TranscriptionError("faster-whisper is not installed.") from exc
        return WhisperModel

    def _validate_runtime_options(self) -> None:
        if self.device == "cpu" and self.compute_type == "float16":
            raise TranscriptionError(
                'Invalid faster-whisper configuration: compute_type="float16" is not supported on device="cpu".'
            )

