from datetime import datetime
from pathlib import Path
import unittest

from app.controllers.workspace_controller import WorkspaceController
from core.errors import FileDeletionError
from core.models import SessionInfo


class WorkspaceControllerTests(unittest.TestCase):
    def test_create_session_delegates_to_session_store_function(self) -> None:
        calls: list[tuple[Path, datetime | None]] = []
        created_at = datetime(2026, 6, 25, 12, 0, 0)
        session = SessionInfo(
            session_id="session-1",
            created_at=created_at,
            paths={"session_dir": Path("sessions/session-1")},
        )

        def create_session(base_dir: str | Path, timestamp: datetime | None) -> SessionInfo:
            calls.append((Path(base_dir), timestamp))
            return session

        controller = WorkspaceController(create_session=create_session)

        actual = controller.create_session(Path("sessions"), created_at)

        self.assertEqual(actual, session)
        self.assertEqual(calls, [(Path("sessions"), created_at)])

    def test_delete_session_delegates_to_session_store_function(self) -> None:
        calls: list[Path] = []

        def delete_session(session_dir: str | Path) -> None:
            calls.append(Path(session_dir))

        controller = WorkspaceController(delete_session=delete_session)

        controller.delete_session(Path("sessions/session-1"))

        self.assertEqual(calls, [Path("sessions/session-1")])

    def test_delete_session_propagates_typed_deletion_errors(self) -> None:
        def delete_session(session_dir: str | Path) -> None:
            raise FileDeletionError(f"could not delete {session_dir}")

        controller = WorkspaceController(delete_session=delete_session)

        with self.assertRaises(FileDeletionError):
            controller.delete_session(Path("sessions/session-1"))


if __name__ == "__main__":
    unittest.main()
