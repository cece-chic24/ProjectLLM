from pathlib import Path
import os
import unittest
from unittest.mock import patch

from app.controllers.note_controller import NoteController, create_note_generator_from_config
from core.errors import (
    AzureOpenAIConfigurationError,
    GeminiConfigurationError,
    NoteGenerationError,
)
from core.models import NoteType, TranscriptResult
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse


class FakeNoteGenerator:
    def __init__(self, response: NoteGenerationResponse | None = None) -> None:
        self.response = response
        self.calls: list[NoteGenerationRequest] = []

    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        self.calls.append(request)
        if self.response is None:
            raise NoteGenerationError("failed")
        return self.response


class FakeUnconfiguredNoteGenerator:
    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        raise AzureOpenAIConfigurationError("missing env")


class FakeUnconfiguredGeminiNoteGenerator:
    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        raise GeminiConfigurationError("missing env")


class FakeGeminiGenerator:
    created = 0

    def __init__(self) -> None:
        self.__class__.created += 1

    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        return NoteGenerationResponse(
            note_type=request.note_type,
            content={"summary": "Gemini"},
            model="fake-gemini",
        )


class NoteControllerTests(unittest.TestCase):
    def test_generate_note_builds_request_and_delegates_to_generator(self) -> None:
        transcript = TranscriptResult(
            source_path=Path("sample.wav"),
            text="Summarize this.",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )
        response = NoteGenerationResponse(
            note_type=NoteType.SUMMARY,
            content={"summary": "Summarize this."},
            model="fake-model",
        )
        generator = FakeNoteGenerator(response)
        controller = NoteController(generator)

        actual = controller.generate_note(transcript, NoteType.SUMMARY)

        self.assertEqual(actual, response)
        self.assertEqual(
            generator.calls,
            [NoteGenerationRequest(transcript=transcript, note_type=NoteType.SUMMARY)],
        )

    def test_generate_note_propagates_typed_note_generation_errors(self) -> None:
        transcript = TranscriptResult(
            source_path=Path("sample.wav"),
            text="Summarize this.",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )
        controller = NoteController(FakeNoteGenerator())

        with self.assertRaises(NoteGenerationError):
            controller.generate_note(transcript, NoteType.SUMMARY)

    def test_generate_note_turns_missing_azure_config_into_readable_generation_error(self) -> None:
        transcript = TranscriptResult(
            source_path=Path("sample.wav"),
            text="Summarize this.",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )
        controller = NoteController(FakeUnconfiguredNoteGenerator())

        with self.assertRaisesRegex(NoteGenerationError, "Add your Azure OpenAI settings to .env"):
            controller.generate_note(transcript, NoteType.SUMMARY)

    def test_generate_note_turns_missing_gemini_config_into_readable_generation_error(self) -> None:
        transcript = TranscriptResult(
            source_path=Path("sample.wav"),
            text="Summarize this.",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )
        controller = NoteController(FakeUnconfiguredGeminiNoteGenerator())

        with self.assertRaisesRegex(NoteGenerationError, "Add your Gemini settings to .env"):
            controller.generate_note(transcript, NoteType.SUMMARY)

    def test_note_provider_env_can_select_gemini_provider(self) -> None:
        transcript = TranscriptResult(
            source_path=Path("sample.wav"),
            text="Summarize this.",
            language="en",
            language_probability=0.9,
            segments=[],
            model_size="base",
            device="cpu",
            compute_type="int8",
        )
        FakeGeminiGenerator.created = 0

        with (
            patch.dict(os.environ, {"NOTE_PROVIDER": "gemini"}, clear=False),
            patch("app.controllers.note_controller.GeminiNoteGenerator", FakeGeminiGenerator),
        ):
            controller = NoteController()
            self.assertEqual(FakeGeminiGenerator.created, 0)
            response = controller.generate_note(transcript, NoteType.SUMMARY)

        self.assertEqual(FakeGeminiGenerator.created, 1)
        self.assertEqual(response.model, "fake-gemini")

    def test_unsupported_note_provider_lists_supported_options(self) -> None:
        with patch.dict(os.environ, {"NOTE_PROVIDER": "unknown"}, clear=False):
            with self.assertRaisesRegex(NoteGenerationError, "azure.*gemini.*fake"):
                create_note_generator_from_config()


if __name__ == "__main__":
    unittest.main()
