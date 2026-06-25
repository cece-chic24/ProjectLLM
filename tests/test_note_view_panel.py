import unittest
from types import SimpleNamespace

from PySide6.QtWidgets import QApplication

from ui.panels.note_view_panel import NoteViewPanel


class FakeExportController:
    def __init__(self) -> None:
        self.calls = []

    def export_note(self, note: object) -> None:
        self.calls.append(note)


class NoteViewPanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._app = QApplication.instance() or QApplication([])

    def test_export_calls_controller(self) -> None:
        controller = FakeExportController()
        panel = NoteViewPanel(controller)
        note = SimpleNamespace(note_type="summary", model="fake", content={"summary": "Hello"})
        panel.set_note(note)

        panel._export_note()

        self.assertEqual(controller.calls, [note])
        self.assertIn('"summary": "Hello"', panel._text_edit.toPlainText())

    def test_set_error_displays_message_and_disables_export(self) -> None:
        controller = FakeExportController()
        panel = NoteViewPanel(controller)
        panel.set_note(SimpleNamespace(note_type="summary", model="fake", content={"summary": "Hello"}))

        panel.set_error("Note generation is not configured.")
        panel._export_note()

        self.assertEqual(panel._meta_label.text(), "Note generation failed.")
        self.assertEqual(panel._text_edit.toPlainText(), "Note generation is not configured.")
        self.assertFalse(panel._export_button.isEnabled())
        self.assertEqual(controller.calls, [])


if __name__ == "__main__":
    unittest.main()
