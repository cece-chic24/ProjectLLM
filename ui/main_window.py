"""Main application window for the Phase 1 workflow."""
from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QSplitter,
    QVBoxLayout,
    QWidget,
)

from app.controllers import Phase1Controllers, SessionInfo, create_phase1_controllers
from transcription.transcript_store import load_transcript
from ui.panels.input_panel import InputPanel
from ui.panels.note_options_panel import NoteOptionsPanel
from ui.panels.note_view_panel import NoteViewPanel
from ui.panels.session_cleanup_dialog import SessionCleanupDialog
from ui.panels.transcript_panel import TranscriptPanel
from ui.workers import BackgroundTask


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
        self._populate_session_picker()

    def _build_ui(self) -> None:
        self._input_panel = InputPanel(
            self._controllers.transcription,
            parent=self,
            task_factory=BackgroundTask,
        )
        self._transcript_panel = TranscriptPanel(parent=self)
        self._note_options_panel = NoteOptionsPanel(self._controllers.note, self)
        self._note_view_panel = NoteViewPanel(self._controllers.export, self)

        # Session row: label | picker | open button | delete button
        self._session_label = QLabel("No active session.", self)

        self._session_picker = QComboBox(self)
        self._session_picker.setMinimumWidth(220)
        self._session_picker.setToolTip("Reopen a past session (read-only)")

        self._open_session_button = QPushButton("Open", self)
        self._open_session_button.setEnabled(False)
        self._open_session_button.clicked.connect(self._open_selected_session)

        self._delete_button = QPushButton("Delete Session", self)
        self._delete_button.setEnabled(False)
        self._delete_button.clicked.connect(self._confirm_delete_session)

        session_row = QHBoxLayout()
        session_row.addWidget(self._session_label, 1)
        session_row.addWidget(QLabel("Past sessions:", self))
        session_row.addWidget(self._session_picker)
        session_row.addWidget(self._open_session_button)
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
        self._note_options_panel.note_failed.connect(self._handle_note_failed)
        self._session_picker.currentIndexChanged.connect(self._on_picker_changed)

    # ------------------------------------------------------------------
    # Session picker helpers
    # ------------------------------------------------------------------

    def _populate_session_picker(self) -> None:
        """Fill the combo box with all past sessions."""
        self._session_picker.blockSignals(True)
        self._session_picker.clear()
        self._session_picker.addItem("— select a session —", userData=None)

        sessions = self._workspace_controller.list_sessions()
        for s in sessions:
            label = s.session_id  # e.g. "2025-06-29_143201"
            self._session_picker.addItem(label, userData=s)

        self._session_picker.blockSignals(False)
        self._open_session_button.setEnabled(False)

    def _on_picker_changed(self, index: int) -> None:
        has_selection = index > 0
        self._open_session_button.setEnabled(has_selection)

    def _open_selected_session(self) -> None:
        index = self._session_picker.currentIndex()
        if index <= 0:
            return
        session: SessionInfo = self._session_picker.itemData(index)
        self._load_past_session(session)

    def _load_past_session(self, session: SessionInfo) -> None:
        """Populate the UI from saved files — no re-running anything."""
        self._current_session = session
        self._session_label.setText(
            f"Session (read-only): {session.session_id}"
        )
        self._delete_button.setEnabled(True)

        # Load transcript if it exists and has content
        transcript_path: Path = session.paths.get(
            "transcript.json", session.paths["session_dir"] / "transcript.json"
        )
        if transcript_path.exists() and transcript_path.stat().st_size > 0:
            try:
                transcript = load_transcript(transcript_path)
                self._transcript_panel.set_transcript(transcript)
                self._note_options_panel.set_transcript(transcript)
            except Exception as exc:
                self._transcript_panel.set_error(
                    f"Could not load transcript: {exc}"
                )

        # Load note if it exists and has content
        note_path: Path = session.paths.get(
            "note.json", session.paths["session_dir"] / "note.json"
        )
        if note_path.exists() and note_path.stat().st_size > 0:
            try:
                raw = json.loads(note_path.read_text(encoding="utf-8"))
                # Display raw JSON in the note panel without a full NoteResult object
                self._note_view_panel.set_raw_note(raw, session_id=session.session_id)
            except Exception as exc:
                self._note_view_panel.set_error(f"Could not load note: {exc}")

    # ------------------------------------------------------------------
    # Existing session lifecycle
    # ------------------------------------------------------------------

    def _ensure_session(self) -> SessionInfo:
        if self._current_session is None:
            self._current_session = self._workspace_controller.create_session()
            self._session_label.setText(
                f"Session: {self._current_session.session_id}"
            )
            self._delete_button.setEnabled(True)
            # Refresh picker so the new session appears
            self._populate_session_picker()
        return self._current_session

    def _get_current_session(self) -> SessionInfo | None:
        return self._current_session

    def _handle_transcript_ready(self, transcript: object) -> None:
        self._transcript_panel.set_transcript(transcript)
        self._note_options_panel.set_transcript(transcript)

    def _handle_note_ready(self, note: object) -> None:
        self._note_view_panel.set_note(note)

    def _handle_note_failed(self, message: str) -> None:
        self._note_view_panel.set_error(message)

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
            self._populate_session_picker()  # refresh after delete