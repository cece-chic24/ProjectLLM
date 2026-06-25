from datetime import datetime, timezone
from pathlib import Path
import unittest

from core.errors import (
    AzureOpenAIConfigurationError,
    ExportError,
    FileDeletionError,
    InvalidMediaFileError,
    NoteGenerationError,
    TranscriptionError,
)
from core.models import (
    AppState,
    NoteType,
    RecordingArtifacts,
    ScreenshotContext,
    TranscriptResult,
    TranscriptSegment,
)


class CoreModelsTests(unittest.TestCase):
    def test_transcript_result_holds_segments_and_runtime_metadata(self) -> None:
        segment = TranscriptSegment(start=0.0, end=1.25, text="hello")
        result = TranscriptResult(
            source_path=Path("sample.wav"),
            text="hello",
            language="en",
            language_probability=0.98,
            segments=[segment],
            model_size="tiny",
            device="cpu",
            compute_type="int8",
        )

        self.assertEqual(result.segments, [segment])
        self.assertEqual(result.source_path, Path("sample.wav"))
        self.assertEqual(result.compute_type, "int8")

    def test_later_phase_artifact_stubs_hold_exact_context_fields(self) -> None:
        captured_at = datetime(2026, 6, 25, 12, 0, tzinfo=timezone.utc)
        screenshot = ScreenshotContext(
            path=Path("data/sessions/one/screenshot.png"),
            captured_at=captured_at,
            elapsed_seconds=3.5,
        )
        artifacts = RecordingArtifacts(
            session_id="one",
            started_at=captured_at,
            ended_at=None,
            audio_path=Path("data/sessions/one/audio.wav"),
            video_path=None,
            manifest_path=Path("data/sessions/one/manifest.json"),
            screenshots=[screenshot],
            transcript_segments=[TranscriptSegment(start=0.0, end=1.0, text="hi")],
        )

        self.assertEqual(artifacts.screenshots[0].path, screenshot.path)
        self.assertEqual(artifacts.transcript_segments[0].text, "hi")

    def test_app_state_tracks_view_and_selection_only(self) -> None:
        state = AppState(
            current_view="transcript",
            selected_session_id="session-1",
            selected_source_path=Path("sample.wav"),
            selected_note_type=NoteType.SUMMARY,
        )

        self.assertEqual(state.current_view, "transcript")
        self.assertIs(state.selected_note_type, NoteType.SUMMARY)

    def test_typed_errors_are_exceptions(self) -> None:
        error_types = [
            InvalidMediaFileError,
            TranscriptionError,
            AzureOpenAIConfigurationError,
            NoteGenerationError,
            ExportError,
            FileDeletionError,
        ]

        self.assertTrue(all(issubclass(error_type, Exception) for error_type in error_types))


if __name__ == "__main__":
    unittest.main()
