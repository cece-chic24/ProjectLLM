"""Generated note display panel."""

from __future__ import annotations

import json
from pathlib import Path

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

    def _export_note(self) -> None:
        if self._note is None:
            return
        self._export_controller.export_note(self._note)

