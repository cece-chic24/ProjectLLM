"""Transcript display panel."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtWidgets import QLabel, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget

from app.controllers import TranscriptionController


class TranscriptPanel(QWidget):
    def __init__(
        self,
        transcription_controller: TranscriptionController | None = None,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self._transcription_controller = transcription_controller
        self._table = QTableWidget(0, 3, self)
        self._table.setHorizontalHeaderLabels(["Start", "End", "Text"])
        self._empty_label = QLabel("No transcript loaded.", self)

        layout = QVBoxLayout(self)
        layout.addWidget(self._empty_label)
        layout.addWidget(self._table)

    def load_transcript(
        self,
        audio_file_path: str | Path,
        model_size: str = "base",
        device: str = "cpu",
        compute_type: str = "int8",
    ) -> None:
        if self._transcription_controller is None:
            raise RuntimeError("No transcription controller is configured.")
        transcript = self._transcription_controller.transcribe(
            audio_file_path,
            model_size=model_size,
            device=device,
            compute_type=compute_type,
        )
        self.set_transcript(transcript)

    def set_transcript(self, transcript: object) -> None:
        segments = getattr(transcript, "segments", [])
        self._table.setRowCount(len(segments))
        for row, segment in enumerate(segments):
            self._table.setItem(row, 0, QTableWidgetItem(f"{getattr(segment, 'start', '')}"))
            self._table.setItem(row, 1, QTableWidgetItem(f"{getattr(segment, 'end', '')}"))
            self._table.setItem(row, 2, QTableWidgetItem(str(getattr(segment, "text", ""))))
        self._empty_label.setVisible(len(segments) == 0)
        self._table.setVisible(True)
