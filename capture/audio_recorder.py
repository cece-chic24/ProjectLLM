"""Microphone audio recording."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from core.errors import AudioRecordingError


def select_input_device(audio_backend: Any) -> int | str | None:
    """Pick a reliable input device, preferring WASAPI over the system default's API."""
    try:
        devices = audio_backend.query_devices()
        hostapis = audio_backend.query_hostapis()
        default_input = audio_backend.default.device[0]
    except Exception:
        return None

    if default_input is None or default_input < 0:
        return None

    default_name = devices[default_input]["name"]

    wasapi_index = None
    for idx, hostapi in enumerate(hostapis):
        if "wasapi" in hostapi["name"].lower():
            wasapi_index = idx
            break

    if wasapi_index is None:
        return default_input

    for idx, dev in enumerate(devices):
        if (
            dev["hostapi"] == wasapi_index
            and dev["max_input_channels"] > 0
            and (dev["name"].startswith(default_name.rstrip()) or default_name.rstrip().startswith(dev["name"].rstrip()))
        ):
            return idx

    return default_input


class MicAudioRecorder:
    """Record microphone input to a WAV file."""

    def __init__(
        self,
        output_path: str | Path,
        *,
        samplerate: int = 44100,
        channels: int = 1,
        dtype: str = "float32",
        device: int | str | None = None,
        audio_backend: Any | None = None,
        file_backend: Any | None = None,
    ) -> None:
        self._output_path = Path(output_path)
        self._samplerate = samplerate
        self._channels = channels
        self._dtype = dtype
        self._device = device
        self._audio_backend = audio_backend
        self._file_backend = file_backend
        self._stream: Any | None = None
        self._file: Any | None = None
        self._level: float = 0.0

    @property
    def current_level(self) -> float:
        """Most recent audio input level, roughly 0.0 (silent) to 1.0 (loud)."""
        return self._level

    def start(self) -> None:
        """Start recording microphone input to the configured WAV path."""
        print(f"MicAudioRecorder.start: requested output {self._output_path}", flush=True)
        if self._stream is not None:
            raise AudioRecordingError("Audio recording is already in progress.")

        print("MicAudioRecorder.start: loading audio backend", flush=True)
        audio_backend = self._load_audio_backend()
        if self._device is None:
            self._device = select_input_device(audio_backend)
            print(f"MicAudioRecorder.start: selected input device {self._device!r}", flush=True)
        print("MicAudioRecorder.start: loading file backend", flush=True)
        file_backend = self._load_file_backend()
        print("MicAudioRecorder.start: checking microphone input device", flush=True)
        self._ensure_input_device(audio_backend)

        print(f"MicAudioRecorder.start: creating output folder {self._output_path.parent}", flush=True)
        self._output_path.parent.mkdir(parents=True, exist_ok=True)

        if self._device is not None:
            try:
                device_info = audio_backend.query_devices(self._device)
                native_rate = int(device_info["default_samplerate"])
                print(f"MicAudioRecorder.start: using device native sample rate {native_rate}", flush=True)
                self._samplerate = native_rate
            except Exception as exc:
                print(f"MicAudioRecorder.start: could not read device sample rate: {exc}", flush=True)

        try:
            print("MicAudioRecorder.start: opening WAV file", flush=True)
            self._file = file_backend.SoundFile(
                self._output_path,
                mode="w",
                samplerate=self._samplerate,
                channels=self._channels,
                subtype="PCM_16",
            )
            print("MicAudioRecorder.start: constructing sounddevice InputStream", flush=True)
            self._stream = audio_backend.InputStream(
                samplerate=self._samplerate,
                channels=self._channels,
                dtype=self._dtype,
                device=self._device,
                callback=self._write_audio,
            )
            print("MicAudioRecorder.start: starting sounddevice stream", flush=True)
            self._stream.start()
            print("MicAudioRecorder.start: stream started", flush=True)
        except Exception as exc:
            print(f"MicAudioRecorder.start: failed: {exc}", flush=True)
            self._close_resources()
            raise AudioRecordingError(f"Failed to start audio recording: {exc}") from exc

    def stop(self) -> None:
        """Stop recording and close the WAV file."""
        print("MicAudioRecorder.stop: requested", flush=True)
        if self._stream is None and self._file is None:
            print("MicAudioRecorder.stop: nothing to stop", flush=True)
            return

        try:
            if self._stream is not None:
                print("MicAudioRecorder.stop: stopping stream", flush=True)
                self._stream.stop()
                print("MicAudioRecorder.stop: closing stream", flush=True)
                self._stream.close()
            if self._file is not None:
                print("MicAudioRecorder.stop: closing WAV file", flush=True)
                self._file.close()
            print("MicAudioRecorder.stop: stopped", flush=True)
        except Exception as exc:
            print(f"MicAudioRecorder.stop: failed: {exc}", flush=True)
            raise AudioRecordingError(f"Failed to stop audio recording: {exc}") from exc
        finally:
            self._stream = None
            self._file = None
            self._level = 0.0

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
        self._update_level(indata)

    def _update_level(self, indata: Any) -> None:
        try:
            import numpy as np
            rms = float(np.sqrt(np.mean(np.square(indata))))
        except Exception:
            rms = 0.0
        self._level = max(0.0, min(rms * 6, 1.0))

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