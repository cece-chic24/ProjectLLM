"""Main application window for the Phase 1 workflow."""

from __future__ import annotations

from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.controllers import Phase1Controllers, SessionInfo, create_phase1_controllers
from ui.panels.input_panel import InputPanel
from ui.panels.note_options_panel import NoteOptionsPanel
from ui.panels.note_view_panel import NoteViewPanel
from ui.panels.session_cleanup_dialog import SessionCleanupDialog
from ui.panels.transcript_panel import TranscriptPanel


class MainWindow(QMainWindow):
    """Thin shell that wires Phase 1 panels to controllers."""

    def __init__(
        self,
        controllers: Phase1Controllers | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._current_session: SessionInfo | None = None
        self._controllers = controllers or create_phase1_controllers(
            self._ensure_session,
            self._get_current_session,
        )
        self._workspace_controller = self._controllers.workspace

        self.setWindowTitle("ProjectLLM")
        self.resize(1100, 760)
        self._build_ui()
        self._connect_signals()

    def _build_ui(self) -> None:
        self._input_panel = InputPanel(self._controllers.transcription, self)
        self._transcript_panel = TranscriptPanel(parent=self)
        self._note_options_panel = NoteOptionsPanel(self._controllers.note, self)
        self._note_view_panel = NoteViewPanel(self._controllers.export, self)

        self._session_label = QLabel("No active session.", self)
        self._delete_button = QPushButton("Delete Session", self)
        self._delete_button.setEnabled(False)
        self._delete_button.clicked.connect(self._confirm_delete_session)

        session_row = QHBoxLayout()
        session_row.addWidget(self._session_label, 1)
        session_row.addWidget(self._delete_button)

        left_column = QWidget(self)
        left_layout = QVBoxLayout(left_column)
        left_layout.addWidget(self._input_panel)
        left_layout.addWidget(self._transcript_panel, 1)

        right_column = QWidget(self)
        right_layout = QVBoxLayout(right_column)
        right_layout.addWidget(self._note_options_panel)
        right_layout.addWidget(self._note_view_panel, 1)

        splitter = QSplitter(self)
        splitter.addWidget(left_column)
        splitter.addWidget(right_column)
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 1)

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.addLayout(session_row)
        layout.addWidget(splitter, 1)
        self.setCentralWidget(central)

    def _connect_signals(self) -> None:
        self._input_panel.transcript_ready.connect(self._handle_transcript_ready)
        self._note_options_panel.note_requested.connect(self._handle_note_ready)

    def _ensure_session(self) -> SessionInfo:
        if self._current_session is None:
            self._current_session = self._workspace_controller.create_session()
            self._session_label.setText(f"Session: {self._current_session.session_id}")
            self._delete_button.setEnabled(True)
        return self._current_session

    def _get_current_session(self) -> SessionInfo | None:
        return self._current_session

    def _handle_transcript_ready(self, transcript: object) -> None:
        self._transcript_panel.set_transcript(transcript)
        self._note_options_panel.set_transcript(transcript)

    def _handle_note_ready(self, note: object) -> None:
        self._note_view_panel.set_note(note)

    def _confirm_delete_session(self) -> None:
        if self._current_session is None:
            return

        dialog = SessionCleanupDialog(
            self._workspace_controller,
            self._current_session,
            self,
        )
        if dialog.exec():
            self._current_session = None
            self._session_label.setText("No active session.")
            self._delete_button.setEnabled(False)
