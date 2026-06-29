"""Audio input panel."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import time

from PySide6.QtCore import Signal, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.controllers import TranscriptionController
from storage.workspace_settings import load_settings, save_settings


KNOWN_BAD_COMPUTE_COMBINATIONS = {("cpu", "float16")}
RecordingTaskFactory = Callable[[Callable[[], Any]], Any]


class InputPanel(QWidget):
    transcript_ready = Signal(object)

    def __init__(
        self,
        transcription_controller: TranscriptionController,
        parent: QWidget | None = None,
        task_factory: RecordingTaskFactory | None = None,
    ) -> None:
        super().__init__(parent)
        self._transcription_controller = transcription_controller
        self._task_factory = task_factory
        self._is_recording = False
        self._recording_task_pending = False
        self._transcribe_task_pending = False
        self._pending_status_message = ""
        self._active_task: Any | None = None

        self._record_start_time: float | None = None

        self._ui_timer = QTimer(self)
        self._ui_timer.setInterval(200)
        self._ui_timer.timeout.connect(self._update_recording_ui)

        self._build_ui()
        self._apply_saved_settings()
        self._refresh_validation()

    def _build_ui(self) -> None:
        self._audio_path_edit = QLineEdit(self)
        self._audio_path_edit.setReadOnly(True)

        browse_button = QPushButton("Browse", self)
        browse_button.clicked.connect(self._browse_audio)

        audio_row = QHBoxLayout()
        audio_row.addWidget(self._audio_path_edit)
        audio_row.addWidget(browse_button)

        self._record_button = QPushButton("Record", self)
        self._record_button.clicked.connect(self._toggle_recording)

        self._level_bar = QProgressBar(self)
        self._level_bar.setRange(0, 100)
        self._level_bar.setValue(0)
        self._level_bar.setTextVisible(False)
        self._level_bar.setFixedHeight(8)

        self._model_combo = QComboBox(self)
        self._model_combo.addItems(["base", "small", "medium", "large-v3"])

        self._device_combo = QComboBox(self)
        self._device_combo.addItems(["cpu", "cuda", "auto"])

        self._compute_type_combo = QComboBox(self)
        self._compute_type_combo.addItems(["int8", "float16", "float32"])

        self._model_combo.currentIndexChanged.connect(self._on_setting_changed)
        self._device_combo.currentIndexChanged.connect(self._on_setting_changed)
        self._compute_type_combo.currentIndexChanged.connect(self._on_setting_changed)

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
        layout.addWidget(self._record_button)
        layout.addWidget(self._level_bar)
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

    def _apply_saved_settings(self) -> None:
        settings = load_settings()
        for combo, key in (
            (self._model_combo, "model"),
            (self._device_combo, "device"),
            (self._compute_type_combo, "compute_type"),
        ):
            idx = combo.findText(settings[key])
            if idx >= 0:
                combo.setCurrentIndex(idx)

    def _on_setting_changed(self) -> None:
        save_settings(
            self._selected_model(),
            self._selected_device(),
            self._selected_compute_type(),
        )
        self._refresh_validation()

    def _selected_model(self) -> str:
        return self._model_combo.currentText()

    def _selected_device(self) -> str:
        return self._device_combo.currentText()

    def _selected_compute_type(self) -> str:
        return self._compute_type_combo.currentText()

    def _is_valid_configuration(self) -> bool:
        return (
            self._selected_device(),
            self._selected_compute_type(),
        ) not in KNOWN_BAD_COMPUTE_COMBINATIONS

    def _refresh_validation(self) -> None:
        if self._recording_task_pending or self._transcribe_task_pending:
            self._status_label.setText(self._pending_status_message)
            self._transcribe_button.setEnabled(False)
            self._record_button.setEnabled(False)
            return

        if self._is_recording:
            self._status_label.setText("Recording...")
            self._transcribe_button.setEnabled(False)
            self._record_button.setEnabled(True)
            return

        self._record_button.setEnabled(self._is_valid_configuration())

        if not self._audio_path_edit.text().strip():
            self._status_label.setText("Choose an audio file.")
            self._transcribe_button.setEnabled(False)
            return

        if not self._is_valid_configuration():
            self._status_label.setText(
                "Selected device and compute type are not allowed together."
            )
            self._transcribe_button.setEnabled(False)
            return

        self._status_label.setText("")
        self._transcribe_button.setEnabled(True)

    def _toggle_recording(self) -> None:
        if self._is_recording:
            self._stop_recording()
        else:
            self._start_recording()

    def _update_recording_ui(self) -> None:
        if self._record_start_time is not None:
            elapsed = int(time.monotonic() - self._record_start_time)
            minutes, seconds = divmod(elapsed, 60)
            self._record_button.setText(f"Stop ({minutes}:{seconds:02d})")

        level = self._transcription_controller.current_recording_level()
        self._level_bar.setValue(int(level * 100))

    def _start_recording(self) -> None:
        if not self._is_valid_configuration():
            self._refresh_validation()
            return

        def work() -> Path:
            return self._transcription_controller.start_recording()

        def on_success(recording_path: object) -> None:
            self._recording_task_pending = False
            self._pending_status_message = ""
            self._active_task = None
            self._audio_path_edit.setText(str(recording_path))
            self._is_recording = True
            self._record_button.setText("Stop")
            self._set_option_controls_enabled(False)

            self._record_start_time = time.monotonic()
            self._ui_timer.start()

            self._refresh_validation()

        def on_failure(exc: object) -> None:
            self._recording_task_pending = False
            self._pending_status_message = ""
            self._active_task = None
            self._status_label.setText(str(exc) or "Audio recording failed.")
            self._refresh_validation()

        self._run_recording_task(
            work,
            on_success,
            on_failure,
            "Starting recording...",
        )

    def _stop_recording(self) -> None:
        model_size = self._selected_model()
        device = self._selected_device()
        compute_type = self._selected_compute_type()

        def work() -> object:
            return self._transcription_controller.stop_recording(
                model_size=model_size,
                device=device,
                compute_type=compute_type,
            )

        def on_success(result: object) -> None:
            self._recording_task_pending = False
            self._pending_status_message = ""
            self._active_task = None
            self._is_recording = False
            self._record_button.setText("Record")
            self._set_option_controls_enabled(True)

            self._ui_timer.stop()
            self._level_bar.setValue(0)

            self._refresh_validation()
            self.transcript_ready.emit(result)

        def on_failure(exc: object) -> None:
            self._recording_task_pending = False
            self._pending_status_message = ""
            self._active_task = None
            self._is_recording = False
            self._record_button.setText("Record")
            self._set_option_controls_enabled(True)

            self._ui_timer.stop()
            self._level_bar.setValue(0)

            self._status_label.setText(str(exc) or "Audio recording failed.")
            self._refresh_validation()

        self._run_recording_task(
            work,
            on_success,
            on_failure,
            "Stopping recording...",
        )

    def _run_recording_task(
        self,
        work: Callable[[], Any],
        on_success: Callable[[object], None],
        on_failure: Callable[[object], None],
        pending_message: str,
    ) -> None:
        if self._task_factory is None:
            try:
                on_success(work())
            except Exception as exc:
                on_failure(exc)
            return

        self._recording_task_pending = True
        self._pending_status_message = pending_message
        self._record_button.setEnabled(False)
        self._transcribe_button.setEnabled(False)
        self._status_label.setText(pending_message)

        task = self._task_factory(work)
        self._active_task = task

        task.finished.connect(on_success)
        task.failed.connect(on_failure)
        task.finished.connect(self._clear_active_task)
        task.failed.connect(self._clear_active_task)

        task.start()

    def _clear_active_task(self, *_: object) -> None:
        self._active_task = None

    def _set_option_controls_enabled(self, enabled: bool) -> None:
        self._model_combo.setEnabled(enabled)
        self._device_combo.setEnabled(enabled)
        self._compute_type_combo.setEnabled(enabled)

    def _transcribe(self) -> None:
        if not self._is_valid_configuration():
            self._refresh_validation()
            return

        audio_path = self._audio_path_edit.text().strip()
        if not audio_path:
            self._refresh_validation()
            return

        model_size = self._selected_model()
        device = self._selected_device()
        compute_type = self._selected_compute_type()

        def work() -> object:
            return self._transcription_controller.transcribe(
                Path(audio_path),
                model_size=model_size,
                device=device,
                compute_type=compute_type,
            )

        def on_success(result: object) -> None:
            self._transcribe_task_pending = False
            self._pending_status_message = ""
            self._active_task = None
            self._set_option_controls_enabled(True)
            self._refresh_validation()
            self.transcript_ready.emit(result)

        def on_failure(exc: object) -> None:
            self._transcribe_task_pending = False
            self._pending_status_message = ""
            self._active_task = None
            self._set_option_controls_enabled(True)
            self._status_label.setText(str(exc) or "Transcription failed.")
            self._refresh_validation()

        if self._task_factory is None:
            try:
                on_success(work())
            except Exception as exc:
                on_failure(exc)
            return

        self._transcribe_task_pending = True
        self._pending_status_message = "Transcribing..."
        self._set_option_controls_enabled(False)
        self._refresh_validation()

        task = self._task_factory(work)
        self._active_task = task
        task.finished.connect(on_success)
        task.failed.connect(on_failure)
        task.finished.connect(self._clear_active_task)
        task.failed.connect(self._clear_active_task)
        task.start()