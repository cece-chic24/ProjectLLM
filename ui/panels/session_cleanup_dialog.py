"""Session cleanup confirmation dialog."""

from __future__ import annotations

from PySide6.QtWidgets import QDialog, QDialogButtonBox, QLabel, QListWidget, QVBoxLayout

from app.controllers import SessionInfo, WorkspaceController


class SessionCleanupDialog(QDialog):
    def __init__(self, workspace_controller: WorkspaceController, session: SessionInfo, parent: QDialog | None = None) -> None:
        super().__init__(parent)
        self._workspace_controller = workspace_controller
        self._session = session

        self._summary_label = QLabel("The following files will be deleted:", self)
        self._file_list = QListWidget(self)
        for name, path in sorted(session.paths.items()):
            self._file_list.addItem(f"{name}: {path}")

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Cancel | QDialogButtonBox.StandardButton.Ok, self)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)

        layout = QVBoxLayout(self)
        layout.addWidget(self._summary_label)
        layout.addWidget(self._file_list)
        layout.addWidget(buttons)

    def accept(self) -> None:
        self._workspace_controller.delete_session(self._session.paths["session_dir"])
        super().accept()
