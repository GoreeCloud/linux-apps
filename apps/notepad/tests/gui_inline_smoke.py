"""Native GTK inline-checkbox and rule regression tests (requires Xvfb)."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gio, Gtk

from goreecloud_notepad.app import NotepadApplication
from goreecloud_notepad.storage import Note


def flush():
    context = GLib.MainContext.default()
    for _ in range(80):
        if not context.pending():
            break
        context.iteration(False)


def main():
    with tempfile.TemporaryDirectory(prefix="gcn-inline-test-") as folder:
        os.environ["XDG_CONFIG_HOME"] = folder
        app = NotepadApplication()
        app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        app.register()
        app.activate()
        window = app.window
        page = window.current()
        note = "# Test\n\n---\n\n- [ ] Write securely\n- [x] Test offline\n"
        page.buffer.set_text(note)
        flush()

        decorations = page.inline
        assert len(decorations.widgets) == 3, type(decorations.widgets)
        checks = [w for w in decorations.widgets if isinstance(w, Gtk.CheckButton)]
        rules = [w for w in decorations.widgets if isinstance(w, Gtk.Separator)]
        assert len(checks) == 2 and len(rules) == 1
        assert [w.get_active() for w in checks] == [False, True]
        assert page.buffer.get_text(*page.buffer.get_bounds(), True) == note

        path = Path(folder) / "note.md"
        page.note.save(path)
        page.refresh_label()
        window.update_status()
        assert path.read_text() == note
        checks[0].set_active(True)
        assert "- [x] Write securely" in page.note.text
        assert page.note.dirty and window.file_status.get_text() == "Unsaved"
        assert path.read_text() == note, "Visual toggle must not auto-save"
        flush()
        assert [w.get_active() for w in decorations.widgets if isinstance(w, Gtk.CheckButton)] == [True, True]
        window.undo_current()
        assert page.note.text == note
        window.redo_current()
        assert "- [x] Write securely" in page.note.text
        page.note.save()
        assert Note.open(path).text == page.note.text
        assert page.buffer.get_text(*page.buffer.get_bounds(), True) == path.read_text()

        # Code fences and oversized content must not create fake controls.
        fenced = "\x60\x60\x60\n- [ ] Not a task\n---\n\x60\x60\x60\n- [ ] Actual task\n"
        page.buffer.set_text(fenced)
        flush()
        assert len(decorations.widgets) == 1
        window._set_live_markdown(False)
        flush()
        assert not decorations.widgets
        assert page.buffer.get_text(*page.buffer.get_bounds(), True) == fenced
        window._set_live_markdown(True)
        flush()
        assert len(decorations.widgets) == 1
        window._set_appearance("dark")
        flush()
        assert decorations.dark
        window._set_appearance("light")
        flush()
        assert not decorations.dark
        decorations.MAX_CHARS = 80
        page.buffer.set_text("x" * 81 + "\n- [ ] Task")
        flush()
        assert not decorations.widgets
        assert page.note.text.endswith("- [ ] Task")

        window._close_confirmed = True
        window.close()
        app.quit()
        print("Native inline Markdown checkbox/rule smoke: PASS")


if __name__ == "__main__":
    main()
