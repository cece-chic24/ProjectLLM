"""Audio input panel."""

from __future__ import annotations

from pathlib import Path

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.controllers.transcription_controller import TranscriptionController


KNOWN_BAD_COMPUTE_COMBINATIONS = {("cpu", "float16")}


class InputPanel(QWidget):
    transcript_ready = Signal(object)

    def __init__(self, transcription_controller: TranscriptionController, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._transcription_controller = transcription_controller
        self._build_ui()
        self._refresh_validation()

    def _build_ui(self) -> None:
        self._audio_path_edit = QLineEdit(self)
        self._audio_path_edit.setReadOnly(True)

        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self._browse_audio)

        audio_row = QHBoxLayout()
        audio_row.addWidget(self._audio_path_edit)
        audio_row.addWidget(browse_button)

        self._model_combo = QComboBox(self)
        self._model_combo.addItems(["base", "small", "medium", "large-v3"])
        self._device_combo = QComboBox(self)
        self._device_combo.addItems(["cpu", "cuda", "auto"])
        self._compute_type_combo = QComboBox(self)
        self._compute_type_combo.addItems(["int8", "float16", "float32"])

        self._model_combo.currentIndexChanged.connect(self._refresh_validation)
        self._device_combo.currentIndexChanged.connect(self._refresh_validation)
        self._compute_type_combo.currentIndexChanged.connect(self._refresh_validation)

        form = QFormLayout()
        form.addRow("Audio file", audio_row)
        form.addRow("Model", self._model_combo)
        form.addRow("Device", self._device_combo)
        form.addRow("Compute type", self._compute_type_combo)

        self._status_label = QLabel(self)
        self._status_label.setWordWrap(True)

        self._transcribe_button = QPushButton("Transcribe", self)
        self._transcribe_button.clicked.connect(self._transcribe)

        layout = QVBoxLayout(self)
        layout.addLayout(form)
        layout.addWidget(self._status_label)
        layout.addWidget(self._transcribe_button)

    def _browse_audio(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select audio file",
            "",
            "Audio Files (*.wav *.mp3 *.m4a *.flac *.ogg);;All Files (*)",
        )
        if path:
            self._audio_path_edit.setText(path)
            self._refresh_validation()

    def _selected_model(self) -> str:
        return self._model_combo.currentText()

    def _selected_device(self) -> str:
        return self._device_combo.currentText()

    def _selected_compute_type(self) -> str:
        return self._compute_type_combo.currentText()

    def _is_valid_configuration(self) -> bool:
        return (self._selected_device(), self._selected_compute_type()) not in KNOWN_BAD_COMPUTE_COMBINATIONS

    def _refresh_validation(self) -> None:
        if not self._audio_path_edit.text().strip():
            self._status_label.setText("Choose an audio file.")
            self._transcribe_button.setEnabled(False)
            return

        if not self._is_valid_configuration():
            self._status_label.setText("Selected device and compute type are not allowed together.")
            self._transcribe_button.setEnabled(False)
            return

        self._status_label.setText("")
        self._transcribe_button.setEnabled(True)

    def _transcribe(self) -> None:
        if not self._is_valid_configuration():
            self._refresh_validation()
            return

        audio_path = self._audio_path_edit.text().strip()
        if not audio_path:
            self._refresh_validation()
            return

        result = self._transcription_controller.transcribe(
            Path(audio_path),
            model_size=self._selected_model(),
            device=self._selected_device(),
            compute_type=self._selected_compute_type(),
        )
        self.transcript_ready.emit(result)

