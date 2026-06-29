"""Persist last-used transcription settings across sessions."""
from __future__ import annotations

import json
from pathlib import Path

_SETTINGS_PATH = Path("data") / "workspace_settings.json"

_DEFAULTS: dict[str, str] = {
    "model": "base",
    "device": "cpu",
    "compute_type": "int8",
}


def load_settings() -> dict[str, str]:
    """Return saved settings, falling back to defaults for any missing key."""
    if not _SETTINGS_PATH.exists():
        return dict(_DEFAULTS)
    try:
        data = json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
        return {k: data.get(k, v) for k, v in _DEFAULTS.items()}
    except Exception:
        return dict(_DEFAULTS)


def save_settings(model: str, device: str, compute_type: str) -> None:
    """Write current settings to disk immediately."""
    _SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    _SETTINGS_PATH.write_text(
        json.dumps(
            {"model": model, "device": device, "compute_type": compute_type},
            indent=2,
        ),
        encoding="utf-8",
    )