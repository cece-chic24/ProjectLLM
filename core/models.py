"""Shared data shapes for ProjectLLM."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from pathlib import Path


class NoteType(StrEnum):
    MEETING = "meeting"
    LECTURE = "lecture"
    TUTORIAL = "tutorial"
    ACTION_ITEMS = "action_items"
    SUMMARY = "summary"
    CUSTOM = "custom"


@dataclass(frozen=True, slots=True)
class TranscriptSegment:
    start: float
    end: float
    text: str


@dataclass(frozen=True, slots=True)
class TranscriptResult:
    source_path: Path
    text: str
    language: str
    language_probability: float
    segments: list[TranscriptSegment]
    model_size: str
    device: str
    compute_type: str


@dataclass(frozen=True, slots=True)
class SessionInfo:
    session_id: str
    created_at: datetime
    paths: dict[str, Path]


@dataclass(frozen=True, slots=True)
class AppState:
    current_view: str
    selected_session_id: str | None = None
    selected_source_path: Path | None = None
    selected_note_type: NoteType | None = None


@dataclass(frozen=True, slots=True)
class ScreenshotContext:
    path: Path
    captured_at: datetime
    elapsed_seconds: float


@dataclass(frozen=True, slots=True)
class RecordingArtifacts:
    session_id: str
    started_at: datetime
    ended_at: datetime | None
    audio_path: Path
    video_path: Path | None
    manifest_path: Path
    screenshots: list[ScreenshotContext] = field(default_factory=list)
    transcript_segments: list[TranscriptSegment] = field(default_factory=list)

