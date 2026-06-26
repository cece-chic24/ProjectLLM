"""Microphone audio recording."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.errors import AudioRecordingError


class MicAudioRecorder:
    """Record microphone input to a WAV file."""

    def __init__(
        self,
        output_path: str | Path,
        *,
        samplerate: int = 44100,
        channels: int = 1,
        dtype: str = "float32",
        audio_backend: Any | None = None,
        file_backend: Any | None = None,
    ) -> None:
        self._output_path = Path(output_path)
        self._samplerate = samplerate
        self._channels = channels
        self._dtype = dtype
        self._audio_backend = audio_backend
        self._file_backend = file_backend
        self._stream: Any | None = None
        self._file: Any | None = None

    def start(self) -> None:
        """Start recording microphone input to the configured WAV path."""
        if self._stream is not None:
            raise AudioRecordingError("Audio recording is already in progress.")

        audio_backend = self._load_audio_backend()
        file_backend = self._load_file_backend()
        self._ensure_input_device(audio_backend)

        self._output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            self._file = file_backend.SoundFile(
                self._output_path,
                mode="w",
                samplerate=self._samplerate,
                channels=self._channels,
                subtype="PCM_16",
            )
            self._stream = audio_backend.InputStream(
                samplerate=self._samplerate,
                channels=self._channels,
                dtype=self._dtype,
                callback=self._write_audio,
            )
            self._stream.start()
        except Exception as exc:
            self._close_resources()
            raise AudioRecordingError(f"Failed to start audio recording: {exc}") from exc

    def stop(self) -> None:
        """Stop recording and close the WAV file."""
        if self._stream is None and self._file is None:
            return

        try:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
            if self._file is not None:
                self._file.close()
        except Exception as exc:
            raise AudioRecordingError(f"Failed to stop audio recording: {exc}") from exc
        finally:
            self._stream = None
            self._file = None

    def _write_audio(
        self,
        indata: Any,
        frames: int,
        time: Any,
        status: Any,
    ) -> None:
        if status:
            raise AudioRecordingError(f"Audio input error: {status}")
        if self._file is None:
            raise AudioRecordingError("Audio recording file is not open.")
        self._file.write(indata)

    def _ensure_input_device(self, audio_backend: Any) -> None:
        try:
            devices = audio_backend.query_devices(kind="input")
        except Exception as exc:
            raise AudioRecordingError("No microphone input device is available.") from exc

        if devices is None:
            raise AudioRecordingError("No microphone input device is available.")

    def _load_audio_backend(self) -> Any:
        if self._audio_backend is not None:
            return self._audio_backend

        try:
            import sounddevice
        except ImportError as exc:
            raise AudioRecordingError("sounddevice is not installed.") from exc
        return sounddevice

    def _load_file_backend(self) -> Any:
        if self._file_backend is not None:
            return self._file_backend

        try:
            import soundfile
        except ImportError as exc:
            raise AudioRecordingError("soundfile is not installed.") from exc
        return soundfile

    def _close_resources(self) -> None:
        if self._stream is not None:
            self._suppress_close(self._stream)
            self._stream = None
        if self._file is not None:
            self._suppress_close(self._file)
            self._file = None

    @staticmethod
    def _suppress_close(resource: Any) -> None:
        try:
            close = getattr(resource, "close", None)
            if close is not None:
                close()
        except Exception:
            pass
