from datetime import datetime
from pathlib import Path
import tempfile
import unittest

from storage.session_store import SESSION_FILENAMES, create_session_folder, delete_session_folder


class SessionStoreTests(unittest.TestCase):
    def test_create_session_folder_uses_expected_layout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            created_at = datetime(2026, 6, 25, 11, 45, 30)
            session = create_session_folder(base_dir=Path(directory), created_at=created_at)
            session_dir = Path(directory) / "2026-06-25_114530"

            self.assertEqual(session.session_id, "2026-06-25_114530")
            self.assertEqual(session.created_at, created_at)
            self.assertTrue(session_dir.is_dir())
            for filename in SESSION_FILENAMES:
                self.assertTrue((session_dir / filename).is_file())
                self.assertEqual(session.paths[filename], session_dir / filename)

    def test_delete_session_folder_removes_folder(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            session = create_session_folder(base_dir=Path(directory), created_at=datetime(2026, 6, 25, 11, 45, 30))
            session_dir = session.paths["session_dir"]

            delete_session_folder(session_dir)

            self.assertFalse(session_dir.exists())


if __name__ == "__main__":
    unittest.main()
