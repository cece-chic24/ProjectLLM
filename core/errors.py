"""Typed application errors for ProjectLLM."""


class InvalidMediaFileError(Exception):
    """Raised when an input media file cannot be accepted."""


class TranscriptionError(Exception):
    """Raised when transcription fails."""


class AzureOpenAIConfigurationError(Exception):
    """Raised when Azure OpenAI configuration is missing or invalid."""


class NoteGenerationError(Exception):
    """Raised when note generation fails."""


class ExportError(Exception):
    """Raised when exporting generated data fails."""


class FileDeletionError(Exception):
    """Raised when deleting an application file fails."""

