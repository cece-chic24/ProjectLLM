import tempfile
import unittest
from pathlib import Path

from scripts.check_secrets import find_secret_lines, scan_files


class CheckSecretsTests(unittest.TestCase):
    def test_placeholder_api_key_is_allowed(self) -> None:
        text = 'AZURE_OPENAI_API_KEY="your-azure-openai-api-key"'

        self.assertEqual(find_secret_lines(text), [])

    def test_real_looking_openai_key_is_blocked(self) -> None:
        text = "OPENAI_API_KEY=" + "sk-" + "abcdefghijklmnopqrstuvwxyz123456"

        self.assertEqual(find_secret_lines(text), [(1, text)])

    def test_scan_files_skips_virtualenv(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            skipped = Path(directory) / ".venv" / "secret.txt"
            skipped.parent.mkdir()
            skipped.write_text("OPENAI_API_KEY=" + "sk-" + "abcdefghijklmnopqrstuvwxyz123456", encoding="utf-8")

            self.assertEqual(scan_files([skipped]), [])


if __name__ == "__main__":
    unittest.main()
