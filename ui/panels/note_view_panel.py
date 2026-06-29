"""Generated note display panel."""

from __future__ import annotations

import json
from pathlib import Path

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QLabel, QPushButton, QTextEdit, QVBoxLayout, QWidget


class NoteViewPanel(QWidget):
    def __init__(self, export_controller: object, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._export_controller = export_controller
        self._note: object | None = None

        self._meta_label = QLabel("No note generated.", self)
        self._text_edit = QTextEdit(self)
        self._text_edit.setReadOnly(True)
        self._export_button = QPushButton("Export", self)
        self._export_button.setEnabled(False)
        self._export_button.clicked.connect(self._export_note)

        layout = QVBoxLayout(self)
        layout.addWidget(self._meta_label)
        layout.addWidget(self._text_edit)
        layout.addWidget(self._export_button)

    def set_note(self, note: object) -> None:
        self._note = note
        note_type = getattr(note, "note_type", None)
        model = getattr(note, "model", None)
        content = getattr(note, "content", {})

        self._meta_label.setText(f"Note type: {note_type} | Model: {model}")
        self._text_edit.setPlainText(json.dumps(content, indent=2, sort_keys=True))
        self._export_button.setEnabled(True)

    def set_raw_note(self, raw: dict, session_id: str = "") -> None:
        """Display a note loaded directly from note.json (no NoteResult object)."""
        self._note = None  # read-only, no export
        label = f"Loaded from session: {session_id}" if session_id else "Loaded from disk"
        self._meta_label.setText(label)
        self._text_edit.setPlainText(json.dumps(raw, indent=2, sort_keys=True))
        self._export_button.setEnabled(False)
        

    def set_error(self, message: str) -> None:
        self._note = None
        self._meta_label.setText("Note generation failed.")
        self._text_edit.setPlainText(message)
        self._export_button.setEnabled(False)

    def _export_note(self) -> None:
        if self._note is None:
            return
        try:
            paths = self._export_controller.export_note(self._note)
            filenames = ", ".join(p.name for p in paths.values())
            self._show_export_feedback(f"Exported: {filenames}", success=True)
        except Exception as exc:
            self._show_export_feedback(f"Export failed: {exc}", success=False)

    def _show_export_feedback(self, message: str, success: bool) -> None:
        original = self._export_button.text()
        self._export_button.setText(message)
        self._export_button.setEnabled(False)
        style = "color: green;" if success else "color: red;"
        self._export_button.setStyleSheet(style)

        def restore() -> None:
            self._export_button.setText(original)
            self._export_button.setEnabled(self._note is not None)
            self._export_button.setStyleSheet("")

        QTimer.singleShot(3000, restore)