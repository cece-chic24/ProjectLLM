import os
import unittest
from unittest.mock import patch

from core.errors import GeminiConfigurationError
from notes.gemini_note_generator import GeminiNoteGenerator


class GeminiNoteGeneratorTests(unittest.TestCase):
    def test_raises_configuration_error_when_required_env_vars_are_absent(self) -> None:
        clean_env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GEMINI_")
        }

        with patch.dict(os.environ, clean_env, clear=True):
            with self.assertRaisesRegex(
                GeminiConfigurationError,
                "GEMINI_API_KEY.*GEMINI_MODEL",
            ):
                GeminiNoteGenerator()

    def test_raises_configuration_error_when_api_key_is_absent(self) -> None:
        clean_env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("GEMINI_")
        }
        clean_env["GEMINI_MODEL"] = "gemini-test-model"

        with patch.dict(os.environ, clean_env, clear=True):
            with self.assertRaisesRegex(GeminiConfigurationError, "GEMINI_API_KEY"):
                GeminiNoteGenerator()


if __name__ == "__main__":
    unittest.main()
