"""Small helpers for running UI-triggered work off the Qt thread."""

from __future__ import annotations

from collections.abc import Callable
from threading import Thread
from typing import Any

from PySide6.QtCore import QObject, Signal


class BackgroundTask(QObject):
    """Run a callable in a daemon thread and report the result through Qt signals."""

    finished = Signal(object)
    failed = Signal(object)

    def __init__(self, work: Callable[[], Any]) -> None:
        super().__init__()
        self._work = work
        self._thread: Thread | None = None

    def start(self) -> None:
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()

    def _run(self) -> None:
        try:
            self.finished.emit(self._work())
        except Exception as exc:
            self.failed.emit(exc)
