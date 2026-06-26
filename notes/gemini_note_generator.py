"""Gemini-backed note generation."""

from __future__ import annotations

import json
import os

from core.errors import GeminiConfigurationError, NoteGenerationError
from notes.base import NoteGenerator
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse
from notes.prompt_builder import build_note_prompt


REQUIRED_ENV_VARS = (
    "GEMINI_API_KEY",
    "GEMINI_MODEL",
)


class GeminiNoteGenerator(NoteGenerator):
    """Generate notes using the Gemini API."""

    def __init__(self) -> None:
        config = _load_required_config()
        self._api_key = config["GEMINI_API_KEY"]
        self._model = config["GEMINI_MODEL"]

    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        prompt = build_note_prompt(request.transcript, request.note_type)

        try:
            import google.generativeai as genai
        except ImportError as exc:
            raise NoteGenerationError("google-generativeai is not installed.") from exc

        try:
            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel(self._model)
            response = model.generate_content(
                prompt,
                generation_config={
                    "response_mime_type": "application/json",
                    "temperature": 0,
                },
            )
            raw_content = response.text
            if raw_content is None:
                raise NoteGenerationError("Gemini returned an empty response.")
            content = json.loads(raw_content)
        except NoteGenerationError:
            raise
        except Exception as exc:
            raise NoteGenerationError(f"Gemini note generation failed: {exc}") from exc

        if not isinstance(content, dict):
            raise NoteGenerationError("Gemini response JSON must be an object.")

        return NoteGenerationResponse(
            note_type=request.note_type,
            content=content,
            model=self._model,
        )


def _load_required_config() -> dict[str, str]:
    values: dict[str, str] = {}
    missing: list[str] = []

    for name in REQUIRED_ENV_VARS:
        value = os.environ.get(name)
        if value is None or not value.strip():
            missing.append(name)
        else:
            values[name] = value

    if missing:
        raise GeminiConfigurationError(
            "Missing required Gemini environment variables: " + ", ".join(missing)
        )

    return values
