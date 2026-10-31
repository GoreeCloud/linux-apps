"""Offline notes and app preferences; no telemetry, network or code execution."""

from __future__ import annotations

import json
import os
import stat
import tempfile
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path

DEFAULTS = {
    "appearance": "light",
    "word_wrap": True,
    "font_size": 15,
    "monospace": False,
    "live_markdown": True,
}
APPEARANCES = ("light", "dark", "system")


class ExternalModificationError(OSError):
    """The note on disk changed; saving would overwrite external edits."""


_CONFLICT_MESSAGE = (
    "File on disk changed, disappeared, or cannot be verified. Your edits remain open. "
    "Use Save As to keep a separate copy, or reopen the note to review its changes."
)


def _read_regular_snapshot(
    path: Path, *, nofollow: bool = False,
) -> tuple[str, tuple[int, int]]:
    """Read a regular UTF-8 file without blocking on an externally swapped FIFO.

    Validate the opened descriptor, rather than trusting a preceding path check.
    The original newline sequences are preserved.
    """
    flags = os.O_RDONLY | os.O_NONBLOCK | getattr(os, "O_CLOEXEC", 0)
    if nofollow:
        flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags)
    with os.fdopen(fd, "r", encoding="utf-8", newline="") as stream:
        info = os.fstat(stream.fileno())
        if not stat.S_ISREG(info.st_mode):
            raise OSError(f"Not a regular note file: {path}")
        return stream.read(), (info.st_dev, info.st_ino)



def _atomic_write(
    path: Path, content: str, *, mode: int | None = None,
    check: Callable[[], None] | None = None,
) -> tuple[int, int]:
    """Stage an atomic write; verify the tracked file immediately before commit."""
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
            info = os.fstat(stream.fileno())
            identity = (info.st_dev, info.st_ino)
        if check is not None:
            check()
        os.replace(temporary, path)
        return identity
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@dataclass
class Note:
    text: str = ""
    path: Path | None = None
    saved_text: str = ""
    file_identity: tuple[int, int] | None = field(default=None, repr=False)

    @property
    def dirty(self) -> bool:
        return self.text != self.saved_text

    @property
    def name(self) -> str:
        return self.path.name if self.path else "Untitled"

    @classmethod
    def open(cls, path: Path) -> "Note":
        path = Path(path).expanduser()
        text, identity = _read_regular_snapshot(path)
        return cls(text=text, path=path, saved_text=text, file_identity=identity)

    def save(self, target: Path | None = None) -> Path:
        destination = Path(target).expanduser() if target is not None else self.path
        if destination is None:
            raise ValueError("Choose a file name first")
        if destination.is_dir():
            raise IsADirectoryError(str(destination))
        if destination.is_symlink():
            raise OSError(f"Refusing to replace symbolic link: {destination}")
        if destination.exists() and not destination.is_file():
            raise OSError(f"Refusing to replace non-file destination: {destination}")

        # Save As to a different path is an explicit user-directed operation.
        tracked = self.path is not None and (
            os.path.abspath(destination) == os.path.abspath(self.path)
        )

        def check_external_change() -> None:
            try:
                on_disk, identity = _read_regular_snapshot(destination, nofollow=True)
            except (OSError, UnicodeError) as exc:
                raise ExternalModificationError(_CONFLICT_MESSAGE) from exc
            if on_disk != self.saved_text or (
                self.file_identity is not None and identity != self.file_identity
            ):
                raise ExternalModificationError(_CONFLICT_MESSAGE)

        if tracked:
            check_external_change()
        current_mode = stat.S_IMODE(destination.stat().st_mode) if destination.exists() else None
        identity = _atomic_write(
            destination, self.text, mode=current_mode,
            check=check_external_change if tracked else None,
        )
        self.path = destination
        self.saved_text = self.text
        self.file_identity = identity
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
        if key in ("word_wrap", "monospace", "live_markdown"):
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
