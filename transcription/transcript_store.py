"""Canonical transcript JSON persistence."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from core.models import TranscriptResult, TranscriptSegment


def save_transcript(result: TranscriptResult, path: str | Path) -> Path:
    """Save a transcript result as canonical JSON."""
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        json.dumps(_transcript_to_dict(result), indent=2),
        encoding="utf-8",
    )
    return destination


def load_transcript(path: str | Path) -> TranscriptResult:
    """Load a transcript result from canonical JSON."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    return _transcript_from_dict(data)


def _transcript_to_dict(result: TranscriptResult) -> dict[str, Any]:
    return {
        "source_path": str(result.source_path),
        "text": result.text,
        "language": result.language,
        "language_probability": result.language_probability,
        "segments": [
            {
                "start": segment.start,
                "end": segment.end,
                "text": segment.text,
            }
            for segment in result.segments
        ],
        "model_size": result.model_size,
        "device": result.device,
        "compute_type": result.compute_type,
    }


def _transcript_from_dict(data: dict[str, Any]) -> TranscriptResult:
    return TranscriptResult(
        source_path=Path(data["source_path"]),
        text=data["text"],
        language=data["language"],
        language_probability=data["language_probability"],
        segments=[
            TranscriptSegment(
                start=segment["start"],
                end=segment["end"],
                text=segment["text"],
            )
            for segment in data["segments"]
        ],
        model_size=data["model_size"],
        device=data["device"],
        compute_type=data["compute_type"],
    )

