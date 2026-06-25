"""Note generation options panel."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QComboBox, QLabel, QPushButton, QVBoxLayout, QWidget

from app.controllers import NoteController, NoteType, TranscriptResult


class NoteOptionsPanel(QWidget):
    note_requested = Signal(object)

    def __init__(self, note_controller: NoteController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._note_controller = note_controller
        self._transcript: TranscriptResult | None = None

        self._type_combo = QComboBox(self)
        for note_type in NoteType:
            self._type_combo.addItem(note_type.value, note_type)

        self._status_label = QLabel("Load a transcript to generate notes.", self)
        self._generate_button = QPushButton("Generate", self)
        self._generate_button.clicked.connect(self._generate_note)
        self._generate_button.setEnabled(False)

        layout = QVBoxLayout(self)
        layout.addWidget(self._type_combo)
        layout.addWidget(self._status_label)
        layout.addWidget(self._generate_button)

    def set_transcript(self, transcript: TranscriptResult) -> None:
        self._transcript = transcript
        self._generate_button.setEnabled(True)
        self._status_label.setText("Ready to generate notes.")

    def _selected_note_type(self) -> NoteType:
        return self._type_combo.currentData()

    def _generate_note(self) -> None:
        if self._transcript is None:
            self._status_label.setText("Load a transcript first.")
            return

        response = self._note_controller.generate_note(self._transcript, self._selected_note_type())
        self.note_requested.emit(response)

