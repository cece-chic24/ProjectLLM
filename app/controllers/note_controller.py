"""Controller for note generation workflows."""

from __future__ import annotations

import os

from core.errors import (
    AzureOpenAIConfigurationError,
    GeminiConfigurationError,
    NoteGenerationError,
)
from core.models import NoteType, TranscriptResult
from notes.azure_openai_note_generator import AzureOpenAINoteGenerator
from notes.base import NoteGenerator
from notes.fake_note_generator import FakeNoteGenerator
from notes.gemini_note_generator import GeminiNoteGenerator
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse


NOTE_PROVIDER_ENV_VAR = "NOTE_PROVIDER"


class NoteController:
    """Thin orchestration layer over a note generator."""

    def __init__(self, note_generator: NoteGenerator | None = None) -> None:
        self._note_generator = note_generator or create_note_generator_from_config()

    def generate_note(
        self,
        transcript: TranscriptResult,
        note_type: NoteType,
    ) -> NoteGenerationResponse:
        request = NoteGenerationRequest(transcript=transcript, note_type=note_type)
        try:
            return self._note_generator.generate(request)
        except AzureOpenAIConfigurationError as exc:
            raise NoteGenerationError(
                "Note generation is not configured. Add your Azure OpenAI settings to .env and restart the app."
            ) from exc
        except GeminiConfigurationError as exc:
            raise NoteGenerationError(
                "Note generation is not configured. Add your Gemini settings to .env and restart the app."
            ) from exc
        except NoteGenerationError:
            raise


class LazyAzureOpenAINoteGenerator(NoteGenerator):
    """Construct the Azure client only when the user generates a note."""

    def __init__(self) -> None:
        self._generator: AzureOpenAINoteGenerator | None = None

    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        if self._generator is None:
            self._generator = AzureOpenAINoteGenerator()
        return self._generator.generate(request)


class LazyGeminiNoteGenerator(NoteGenerator):
    """Construct the Gemini client only when the user generates a note."""

    def __init__(self) -> None:
        self._generator: GeminiNoteGenerator | None = None

    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        if self._generator is None:
            self._generator = GeminiNoteGenerator()
        return self._generator.generate(request)


def create_note_generator_from_config() -> NoteGenerator:
    provider = os.environ.get(NOTE_PROVIDER_ENV_VAR, "azure").strip().lower()
    if provider in {"azure", "azure_openai"}:
        return LazyAzureOpenAINoteGenerator()
    if provider == "gemini":
        return LazyGeminiNoteGenerator()
    if provider in {"fake", "sample"}:
        return FakeNoteGenerator()
    raise NoteGenerationError(
        f"Unsupported note provider {provider!r}. Set {NOTE_PROVIDER_ENV_VAR} to 'azure', 'gemini', or 'fake'."
    )
