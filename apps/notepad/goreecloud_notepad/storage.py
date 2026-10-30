"""Offline notes and app preferences; no telemetry, network or code execution."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from dataclasses import dataclass
from pathlib import Path

DEFAULTS = {
    "appearance": "light",
    "word_wrap": True,
    "font_size": 15,
    "monospace": False,
}
APPEARANCES = ("light", "dark", "system")


def _atomic_write(path: Path, content: str, *, mode: int | None = None) -> None:
    """Write beside the target, then replace atomically; clean up failed writes."""
    path = Path(path)
    if not path.parent.is_dir():
        raise FileNotFoundError(f"Folder not found: {path.parent}")
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        if mode is not None:
            os.fchmod(fd, mode)
        with os.fdopen(fd, "w", encoding="utf-8", newline="") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@dataclass
class Note:
    text: str = ""
    path: Path | None = None
    saved_text: str = ""

    @property
    def dirty(self) -> bool:
        return self.text != self.saved_text

    @property
    def name(self) -> str:
        return self.path.name if self.path else "Untitled"

    @classmethod
    def open(cls, path: Path) -> "Note":
        path = Path(path).expanduser()
        # UTF-8 only: report decode errors rather than silently corrupting files.
        with path.open("r", encoding="utf-8", newline="") as stream:
            text = stream.read()
        return cls(text=text, path=path, saved_text=text)

    def save(self, target: Path | None = None) -> Path:
        destination = Path(target).expanduser() if target is not None else self.path
        if destination is None:
            raise ValueError("Choose a file name first")
        if destination.is_dir():
            raise IsADirectoryError(str(destination))
        current_mode = stat.S_IMODE(destination.stat().st_mode) if destination.exists() else None
        _atomic_write(destination, self.text, mode=current_mode)
        self.path = destination
        self.saved_text = self.text
        return destination


class Preferences:
    def __init__(self, config_path: Path | None = None):
        base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
        self.path = config_path or base / "goreecloud" / "notepad" / "settings.json"
        self._values = dict(DEFAULTS)
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                for key in DEFAULTS:
                    self._values[key] = self._validate(key, raw.get(key, DEFAULTS[key]))
        except (OSError, ValueError, UnicodeError):
            # Invalid configuration is ignored; it is never executed or overwritten on read.
            pass

    @staticmethod
    def _validate(key: str, value):
        if key == "appearance":
            return value if value in APPEARANCES else DEFAULTS[key]
        if key in ("word_wrap", "monospace"):
            return value if isinstance(value, bool) else DEFAULTS[key]
        if key == "font_size":
            return value if type(value) is int and 11 <= value <= 26 else DEFAULTS[key]
        raise KeyError(key)

    def get(self, key: str):
        return self._values[key]

    def set(self, key: str, value) -> None:
        self._values[key] = self._validate(key, value)
        self.path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        _atomic_write(self.path, json.dumps(self._values, indent=2) + "\n", mode=0o600)
