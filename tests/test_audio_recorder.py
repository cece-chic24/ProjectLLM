from pathlib import Path
import tempfile
import unittest

from capture.audio_recorder import MicAudioRecorder
from core.errors import AudioRecordingError


class FakeStream:
    def __init__(self, callback) -> None:
        self._callback = callback
        self.started = False
        self.stopped = False
        self.closed = False

    def start(self) -> None:
        self.started = True
        self._callback([[0.1], [0.2]], 2, None, None)

    def stop(self) -> None:
        self.stopped = True

    def close(self) -> None:
        self.closed = True


class FakeAudioBackend:
    def __init__(self, *, input_available: bool = True) -> None:
        self.input_available = input_available
        self.streams: list[FakeStream] = []

    def query_devices(self, kind: str | None = None):
        if not self.input_available:
            raise RuntimeError("no input device")
        return {"name": "Fake microphone", "max_input_channels": 1}

    def InputStream(self, **kwargs):
        stream = FakeStream(kwargs["callback"])
        self.streams.append(stream)
        return stream


class FakeSoundFile:
    def __init__(self, path: Path, **kwargs) -> None:
        self.path = Path(path)
        self.kwargs = kwargs
        self.writes = []
        self.closed = False

    def write(self, data) -> None:
        self.writes.append(data)

    def close(self) -> None:
        self.closed = True


class FakeFileBackend:
    def __init__(self) -> None:
        self.files: list[FakeSoundFile] = []

    def SoundFile(self, path: Path, **kwargs):
        file = FakeSoundFile(path, **kwargs)
        self.files.append(file)
        return file


class MicAudioRecorderTests(unittest.TestCase):
    def test_start_records_microphone_blocks_to_wav_file_and_stop_closes_resources(self) -> None:
        audio_backend = FakeAudioBackend()
        file_backend = FakeFileBackend()

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "session" / "mic.wav"
            recorder = MicAudioRecorder(
                output_path,
                audio_backend=audio_backend,
                file_backend=file_backend,
            )

            recorder.start()
            recorder.stop()

        self.assertEqual(len(file_backend.files), 1)
        self.assertEqual(file_backend.files[0].path, output_path)
        self.assertEqual(file_backend.files[0].kwargs["mode"], "w")
        self.assertEqual(file_backend.files[0].kwargs["samplerate"], 44100)
        self.assertEqual(file_backend.files[0].kwargs["channels"], 1)
        self.assertEqual(file_backend.files[0].kwargs["subtype"], "PCM_16")
        self.assertEqual(file_backend.files[0].writes, [[[0.1], [0.2]]])
        self.assertTrue(file_backend.files[0].closed)
        self.assertTrue(audio_backend.streams[0].started)
        self.assertTrue(audio_backend.streams[0].stopped)
        self.assertTrue(audio_backend.streams[0].closed)

    def test_start_raises_typed_error_when_no_input_device_is_available(self) -> None:
        recorder = MicAudioRecorder(
            "mic.wav",
            audio_backend=FakeAudioBackend(input_available=False),
            file_backend=FakeFileBackend(),
        )

        with self.assertRaisesRegex(AudioRecordingError, "No microphone input device"):
            recorder.start()


if __name__ == "__main__":
    unittest.main()
