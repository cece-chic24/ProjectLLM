"""Controller for transcription workflows."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from capture.audio_recorder import MicAudioRecorder
from core.errors import AudioRecordingError, TranscriptionError
from core.models import SessionInfo, TranscriptResult
from transcription.base import TranscriptionProvider


TranscriptionFactory = Callable[..., TranscriptionProvider]
BeforeTranscribe = Callable[[], SessionInfo]
AudioRecorderFactory = Callable[[Path], MicAudioRecorder]


class TranscriptionController:
    """Thin orchestration layer over a transcription provider."""

    def __init__(
        self,
        transcription_provider: TranscriptionProvider | None = None,
        transcription_factory: TranscriptionFactory | None = None,
        before_transcribe: BeforeTranscribe | None = None,
        audio_recorder_factory: AudioRecorderFactory = MicAudioRecorder,
    ) -> None:
        self._transcription_provider = transcription_provider
        self._transcription_factory = transcription_factory
        self._before_transcribe = before_transcribe
        self._audio_recorder_factory = audio_recorder_factory
        self._audio_recorder: MicAudioRecorder | None = None
        self._recording_path: Path | None = None

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

    def start_recording(self) -> Path:
        print("TranscriptionController.start_recording: requested", flush=True)
        if self._audio_recorder is not None:
            raise AudioRecordingError("Audio recording is already in progress.")
        if self._before_transcribe is None:
            raise AudioRecordingError("No session provider is configured for recording.")

        print("TranscriptionController.start_recording: ensuring session", flush=True)
        session = self._before_transcribe()
        recording_path = session.paths["session_dir"] / "recording.wav"
        print(f"TranscriptionController.start_recording: recording path {recording_path}", flush=True)
        print("TranscriptionController.start_recording: creating recorder", flush=True)
        recorder = self._audio_recorder_factory(recording_path)
        print("TranscriptionController.start_recording: starting recorder", flush=True)
        recorder.start()
        print("TranscriptionController.start_recording: recorder started", flush=True)
        self._audio_recorder = recorder
        self._recording_path = recording_path
        return recording_path

    def stop_recording(
        self,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> TranscriptResult:
        print("TranscriptionController.stop_recording: requested", flush=True)
        if self._audio_recorder is None or self._recording_path is None:
            raise AudioRecordingError("No audio recording is in progress.")

        recording_path = self._recording_path
        recorder = self._audio_recorder
        self._audio_recorder = None
        self._recording_path = None
        print("TranscriptionController.stop_recording: stopping recorder", flush=True)
        recorder.stop()
        print(f"TranscriptionController.stop_recording: transcribing {recording_path}", flush=True)
        return self.transcribe(
            recording_path,
            model_size=model_size,
            device=device,
            compute_type=compute_type,
        )

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
