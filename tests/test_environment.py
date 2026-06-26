import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from app.controllers.note_controller import create_note_generator_from_config
from core.environment import load_project_dotenv
from notes.fake_note_generator import FakeNoteGenerator


class EnvironmentLoadingTests(unittest.TestCase):
    def test_load_project_dotenv_sets_provider_before_controller_config_is_read(self) -> None:
        clean_env = {key: value for key, value in os.environ.items() if key != "NOTE_PROVIDER"}

        with tempfile.TemporaryDirectory() as temp_dir:
            dotenv_path = Path(temp_dir) / ".env"
            dotenv_path.write_text('NOTE_PROVIDER="fake"\n', encoding="utf-8")

            with patch.dict(os.environ, clean_env, clear=True):
                loaded = load_project_dotenv(dotenv_path)
                generator = create_note_generator_from_config()
                self.assertEqual(os.environ["NOTE_PROVIDER"], "fake")

        self.assertTrue(loaded)
        self.assertIsInstance(generator, FakeNoteGenerator)


if __name__ == "__main__":
    unittest.main()
