"""Data shapes for speaker diarisation (Phase 3 groundwork)."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import timedelta


@dataclass(frozen=True)
class SpeakerTurn:
    """A single continuous segment of one speaker talking."""

    speaker_id: str
    start: float  # seconds
    end: float    # seconds

    @property
    def duration(self) -> float:
        return self.end - self.start

    @property
    def start_td(self) -> timedelta:
        return timedelta(seconds=self.start)

    @property
    def end_td(self) -> timedelta:
        return timedelta(seconds=self.end)


@dataclass(frozen=True)
class SpeakerIdentity:
    """A resolved speaker with optional human-readable name."""

    speaker_id: str
    display_name: str | None = None

    @property
    def label(self) -> str:
        return self.display_name or self.speaker_id


@dataclass(frozen=True)
class SpeakerClusterAssignment:
    """Maps a raw cluster ID from diarisation to a SpeakerIdentity."""

    cluster_id: str
    identity: SpeakerIdentity


@dataclass
class SpeakerAnnotatedSegment:
    """A transcript segment enriched with speaker attribution."""

    start: float
    end: float
    text: str
    speaker: SpeakerIdentity | None = None

    @property
    def attributed_text(self) -> str:
        prefix = f"[{self.speaker.label}] " if self.speaker else ""
        return f"{prefix}{self.text}"