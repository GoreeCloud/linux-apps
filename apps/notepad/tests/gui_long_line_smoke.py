"""Native GTK4 fast-wrap fallback for exceptionally long tokens."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk

from goreecloud_notepad.app import NotepadApplication


def flush():
    context = GLib.MainContext.default()
    for _ in range(100):
        if not context.pending():
            break
        context.iteration(False)


def main():
    with tempfile.TemporaryDirectory(prefix="gcn-wrap-test-") as folder:
        os.environ["XDG_CONFIG_HOME"] = folder
        app = NotepadApplication()
        app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        app.register()
        app.activate()
        window = app.window
        page = window.current()

        assert page.editor.get_wrap_mode() == Gtk.WrapMode.WORD_CHAR
        assert window.wrap_status.get_text() == "Wrap: On"

        exceptional = "a" * 5000
        page.buffer.set_text(exceptional)
        flush()
        assert page.editor.get_wrap_mode() == Gtk.WrapMode.CHAR
        assert window.wrap_status.get_text() == "Wrap: Fast"
        assert page.note.text == exceptional

        original = Path(folder) / "exact-source.md"
        page.note.save(original)
        assert original.read_bytes() == exceptional.encode("utf-8")

        page.buffer.set_text("ordinary words " * 250)
        flush()
        assert page.editor.get_wrap_mode() == Gtk.WrapMode.WORD_CHAR
        assert window.wrap_status.get_text() == "Wrap: On"

        window._set_wrap(False)
        page.buffer.set_text(exceptional)
        flush()
        assert page.editor.get_wrap_mode() == Gtk.WrapMode.NONE
        assert window.wrap_status.get_text() == "Wrap: Off"

        window._set_wrap(True)
        flush()
        assert page.editor.get_wrap_mode() == Gtk.WrapMode.CHAR
        assert page.note.text == exceptional

        # Reducing an extreme token must restore the normal word-wrap mode.
        page.buffer.set_text("short text")
        flush()
        assert page.editor.get_wrap_mode() == Gtk.WrapMode.WORD_CHAR
        assert window.wrap_status.get_text() == "Wrap: On"

        window._close_confirmed = True
        window.close()
        app.quit()
        print("Native long-token GTK4 fast-wrap smoke: PASS")


if __name__ == "__main__":
    main()
