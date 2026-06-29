"""Record a short microphone sample and report its amplitude levels."""

from __future__ import annotations

import argparse
import sys
import tempfile
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from capture.audio_recorder import MicAudioRecorder


def parse_device(value: str | None) -> int | str | None:
    if value is None:
        return None
    try:
        return int(value)
    except ValueError:
        return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Record 3 seconds from a microphone device and report levels.")
    parser.add_argument("--device", default=None, help="Device index or name passed to sounddevice.InputStream.")
    parser.add_argument("--seconds", type=float, default=3.0, help="Recording duration in seconds.")
    parser.add_argument("--samplerate", type=int, default=44100, help="Audio sample rate.")
    parser.add_argument("--channels", type=int, default=1, help="Number of input channels.")
    args = parser.parse_args()

    device = parse_device(args.device)

    with tempfile.TemporaryDirectory() as temp_dir:
        output_path = Path(temp_dir) / "microphone_probe.wav"
        recorder = MicAudioRecorder(
            output_path,
            samplerate=args.samplerate,
            channels=args.channels,
            device=device,
        )

        recorder.start()
        print(f"Recording {args.seconds:.1f} seconds from device {device!r} to {output_path}")
        time.sleep(args.seconds)
        recorder.stop()

        import soundfile as sf

        samples, _ = sf.read(output_path, dtype="float32", always_2d=True)
        if samples.size == 0:
            print("No samples were captured.")
            return 1

        peak = float(np.max(np.abs(samples)))
        rms = float(np.sqrt(np.mean(np.square(samples))))

        print(f"Saved sample: {output_path}")
        print(f"Device: {device!r}")
        print(f"Peak amplitude: {peak:.6f}")
        print(f"RMS level: {rms:.6f}")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())