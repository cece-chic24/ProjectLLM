"""Azure OpenAI-backed note generation."""

from __future__ import annotations

import json
import os

from core.errors import AzureOpenAIConfigurationError, NoteGenerationError
from notes.base import NoteGenerator
from notes.note_types import NoteGenerationRequest, NoteGenerationResponse
from notes.prompt_builder import build_note_prompt


DEFAULT_AZURE_OPENAI_API_VERSION = "2024-02-15-preview"
REQUIRED_ENV_VARS = (
    "AZURE_OPENAI_ENDPOINT",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_DEPLOYMENT",
)


class AzureOpenAINoteGenerator(NoteGenerator):
    """Generate notes using Azure OpenAI chat completions."""

    def __init__(self) -> None:
        config = _load_required_config()
        self._endpoint = config["AZURE_OPENAI_ENDPOINT"]
        self._api_key = config["AZURE_OPENAI_API_KEY"]
        self._deployment = config["AZURE_OPENAI_DEPLOYMENT"]
        self._api_version = os.environ.get(
            "AZURE_OPENAI_API_VERSION",
            DEFAULT_AZURE_OPENAI_API_VERSION,
        )

    def generate(self, request: NoteGenerationRequest) -> NoteGenerationResponse:
        prompt = build_note_prompt(request.transcript, request.note_type)

        try:
            from openai import AzureOpenAI
        except ImportError as exc:
            raise NoteGenerationError("openai is not installed.") from exc

        client = AzureOpenAI(
            azure_endpoint=self._endpoint,
            api_key=self._api_key,
            api_version=self._api_version,
        )

        try:
            completion = client.chat.completions.create(
                model=self._deployment,
                messages=[
                    {
                        "role": "system",
                        "content": "You generate source-faithful structured JSON notes.",
                    },
                    {"role": "user", "content": prompt},
                ],
                response_format={"type": "json_object"},
                temperature=0,
            )
            raw_content = completion.choices[0].message.content
            if raw_content is None:
                raise NoteGenerationError("Azure OpenAI returned an empty response.")
            content = json.loads(raw_content)
        except NoteGenerationError:
            raise
        except Exception as exc:
            raise NoteGenerationError(f"Azure OpenAI note generation failed: {exc}") from exc

        if not isinstance(content, dict):
            raise NoteGenerationError("Azure OpenAI response JSON must be an object.")

        return NoteGenerationResponse(
            note_type=request.note_type,
            content=content,
            model=self._deployment,
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
        raise AzureOpenAIConfigurationError(
            "Missing required Azure OpenAI environment variables: "
            + ", ".join(missing)
        )

    return values
