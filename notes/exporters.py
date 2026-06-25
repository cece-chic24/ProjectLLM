"""Note export helpers for generated note payloads."""

from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path
from typing import Any

from core.errors import ExportError


def export_note(note: object, destination: str | Path) -> Path:
    """Export a generated note to .json, .md, or .txt."""
    output_path = Path(destination)
    suffix = output_path.suffix.lower()

    if suffix == ".json":
        return export_note_json(note, output_path)
    elif suffix == ".md":
        return export_note_markdown(note, output_path)
    elif suffix == ".txt":
        return export_note_text(note, output_path)
    else:
        raise ExportError(
            f"Unsupported note export format: {output_path.suffix or '<none>'}."
        )


def export_note_json(note: object, destination: str | Path) -> Path:
    """Export a generated note to the session note.json file."""
    return _write_export(render_note_json(note), destination)


def export_note_markdown(note: object, destination: str | Path) -> Path:
    """Export a generated note to the session note.md file."""
    return _write_export(render_note_markdown(note), destination)


def export_note_text(note: object, destination: str | Path) -> Path:
    """Export a generated note to the session note.txt file."""
    return _write_export(render_note_text(note), destination)


def _write_export(content: str, destination: str | Path) -> Path:
    output_path = Path(destination)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(content, encoding="utf-8")
    return output_path


def render_note_json(note: object) -> str:
    """Render a generated note as canonical JSON."""
    payload = _coerce_note(note)
    return json.dumps(payload, indent=2, sort_keys=True)


def render_note_markdown(note: object) -> str:
    """Render a generated note as Markdown."""
    payload = _coerce_note(note)
    lines = [
        f"# {_humanize_label(payload['note_type'])}",
    ]

    if payload["model"] is not None:
        lines.extend(["", f"- Model: {payload['model']}"])

    lines.extend(["", "## Content"])
    lines.extend(_render_content(payload["content"], markdown=True, level=3))
    return "\n".join(lines).rstrip() + "\n"


def render_note_text(note: object) -> str:
    """Render a generated note as plain text."""
    payload = _coerce_note(note)
    lines = [
        f"Note type: {payload['note_type']}",
    ]

    if payload["model"] is not None:
        lines.append(f"Model: {payload['model']}")

    lines.extend(["", "Content:"])
    lines.extend(_render_content(payload["content"], markdown=False, level=0))
    return "\n".join(lines).rstrip() + "\n"


def _coerce_note(note: object) -> dict[str, Any]:
    note_type = _extract_value(note, "note_type")
    model = _extract_value(note, "model")
    content = _extract_value(note, "content")

    if content is None or not isinstance(content, Mapping):
        raise ExportError("Note content must be a mapping to export.")

    return {
        "note_type": _note_type_value(note_type),
        "model": None if model is None else str(model),
        "content": dict(content),
    }


def _extract_value(note: object, attribute: str) -> Any:
    if isinstance(note, Mapping):
        return note.get(attribute)
    return getattr(note, attribute, None)


def _note_type_value(value: object) -> str:
    if value is None:
        raise ExportError("Note type is required to export a note.")
    raw_value = getattr(value, "value", value)
    return str(raw_value)


def _humanize_label(value: object) -> str:
    return str(value).replace("_", " ").strip().title()


def _render_content(value: object, *, markdown: bool, level: int) -> list[str]:
    if isinstance(value, Mapping):
        lines: list[str] = []
        for key, nested_value in value.items():
            label = _humanize_label(key)
            if markdown:
                lines.append(f"{'#' * level} {label}")
                lines.extend(_render_content(nested_value, markdown=markdown, level=level + 1))
            else:
                lines.append(f"{label}:")
                lines.extend(_render_content(nested_value, markdown=markdown, level=level + 1))
        return lines

    if isinstance(value, list):
        lines = []
        if not value:
            lines.append("- []" if markdown else "[]")
            return lines

        for item in value:
            if isinstance(item, (Mapping, list)):
                lines.extend(_render_content(item, markdown=markdown, level=level + 1))
            else:
                prefix = "- " if markdown or level == 0 else f"{'  ' * level}- "
                lines.append(f"{prefix}{item}")
        return lines

    if value is None:
        return ["None"]

    return [str(value)]
