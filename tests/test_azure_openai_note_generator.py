import os
import unittest
from unittest.mock import patch

from core.errors import AzureOpenAIConfigurationError
from notes.azure_openai_note_generator import AzureOpenAINoteGenerator


class AzureOpenAINoteGeneratorTests(unittest.TestCase):
    def test_raises_configuration_error_when_required_env_vars_are_absent(self) -> None:
        clean_env = {
            key: value
            for key, value in os.environ.items()
            if not key.startswith("AZURE_OPENAI_")
        }

        with patch.dict(os.environ, clean_env, clear=True):
            with self.assertRaisesRegex(
                AzureOpenAIConfigurationError,
                "AZURE_OPENAI_ENDPOINT.*AZURE_OPENAI_API_KEY.*AZURE_OPENAI_DEPLOYMENT",
            ):
                AzureOpenAINoteGenerator()


if __name__ == "__main__":
    unittest.main()
