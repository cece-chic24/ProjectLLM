from pathlib import Path
from datetime import datetime
import unittest

from PySide6.QtWidgets import QApplication

from app.controllers import SessionInfo
from ui.panels.session_cleanup_dialog import SessionCleanupDialog


class FakeWorkspaceController:
    def __init__(self) -> None:
        self.calls = []

    def delete_session(self, session_dir: str | Path) -> None:
        self.calls.append(Path(session_dir))


class SessionCleanupDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_lists_all_files_and_calls_controller_on_accept(self) -> None:
        session = SessionInfo(
            session_id="session-1",
            created_at=datetime(2026, 6, 25, 12, 0, 0),
            paths={
                "session_dir": Path("data/sessions/session-1"),
                "source_info.json": Path("data/sessions/session-1/source_info.json"),
                "transcript.json": Path("data/sessions/session-1/transcript.json"),
            },
        )
        controller = FakeWorkspaceController()
        dialog = SessionCleanupDialog(controller, session)

        self.assertEqual(dialog._file_list.count(), 3)
        dialog.accept()

        self.assertEqual(controller.calls, [Path("data/sessions/session-1")])


if __name__ == "__main__":
    unittest.main()
