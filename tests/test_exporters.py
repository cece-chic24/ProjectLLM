from pathlib import Path
import json
import tempfile
import unittest

from core.errors import ExportError
from core.models import NoteType
from notes.exporters import (
    export_note,
    export_note_json,
    export_note_markdown,
    export_note_text,
    render_note_json,
    render_note_markdown,
    render_note_text,
)
from notes.note_types import NoteGenerationResponse


class ExporterTests(unittest.TestCase):
    def setUp(self) -> None:
        self.note = NoteGenerationResponse(
            note_type=NoteType.ACTION_ITEMS,
            content={
                "summary": "Review the release checklist.",
                "items": ["Ship documentation", "Confirm deployment"],
                "details": {
                    "owner": "Ada",
                    "priority": "High",
                },
            },
            model="fake-model",
        )

    def test_render_note_json_serializes_canonical_payload(self) -> None:
        payload = json.loads(render_note_json(self.note))

        self.assertEqual(
            payload,
            {
                "content": {
                    "details": {"owner": "Ada", "priority": "High"},
                    "items": ["Ship documentation", "Confirm deployment"],
                    "summary": "Review the release checklist.",
                },
                "model": "fake-model",
                "note_type": "action_items",
            },
        )

    def test_render_note_markdown_and_text_include_note_metadata(self) -> None:
        markdown = render_note_markdown(self.note)
        text = render_note_text(self.note)

        self.assertIn("# Action Items", markdown)
        self.assertIn("- Model: fake-model", markdown)
        self.assertIn("## Content", markdown)
        self.assertIn("### Summary", markdown)
        self.assertIn("Review the release checklist.", markdown)

        self.assertIn("Note type: action_items", text)
        self.assertIn("Model: fake-model", text)
        self.assertIn("Summary:", text)
        self.assertIn("Ship documentation", text)

    def test_export_note_json_writes_valid_session_json(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session" / "note.json"

            written_path = export_note_json(self.note, path)

            self.assertEqual(written_path, path)
            self.assertEqual(
                json.loads(path.read_text(encoding="utf-8")),
                {
                    "content": {
                        "details": {"owner": "Ada", "priority": "High"},
                        "items": ["Ship documentation", "Confirm deployment"],
                        "summary": "Review the release checklist.",
                    },
                    "model": "fake-model",
                    "note_type": "action_items",
                },
            )

    def test_export_note_markdown_writes_formatted_session_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session" / "note.md"

            written_path = export_note_markdown(self.note, path)

            self.assertEqual(written_path, path)
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "\n".join(
                    [
                        "# Action Items",
                        "",
                        "- Model: fake-model",
                        "",
                        "## Content",
                        "### Summary",
                        "Review the release checklist.",
                        "### Items",
                        "- Ship documentation",
                        "- Confirm deployment",
                        "### Details",
                        "#### Owner",
                        "Ada",
                        "#### Priority",
                        "High",
                        "",
                    ]
                ),
            )

    def test_export_note_text_writes_formatted_session_text(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "session" / "note.txt"

            written_path = export_note_text(self.note, path)

            self.assertEqual(written_path, path)
            self.assertEqual(
                path.read_text(encoding="utf-8"),
                "\n".join(
                    [
                        "Note type: action_items",
                        "Model: fake-model",
                        "",
                        "Content:",
                        "Summary:",
                        "Review the release checklist.",
                        "Items:",
                        "  - Ship documentation",
                        "  - Confirm deployment",
                        "Details:",
                        "Owner:",
                        "Ada",
                        "Priority:",
                        "High",
                        "",
                    ]
                ),
            )

    def test_export_note_writes_supported_formats_by_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            base_path = Path(directory) / "exports" / "note"

            self.assertEqual(export_note(self.note, base_path.with_suffix(".json")).name, "note.json")
            self.assertEqual(export_note(self.note, base_path.with_suffix(".md")).name, "note.md")
            self.assertEqual(export_note(self.note, base_path.with_suffix(".txt")).name, "note.txt")

    def test_export_note_rejects_unsupported_extension(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.pdf"

            with self.assertRaises(ExportError):
                export_note(self.note, path)


if __name__ == "__main__":
    unittest.main()
