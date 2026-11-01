"""Native GTK4 accessibility roles, focus, state, and Markdown integrity checks."""
import os
import sys
import tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Gio, GLib
from goreecloud_notepad.app import NotepadApplication


def flush():
    ctx = GLib.MainContext.default()
    for _ in range(100):
        if not ctx.pending():
            break
        ctx.iteration(False)


def main():
    with tempfile.TemporaryDirectory(prefix="gcn-a11y-smoke-") as folder:
        os.environ["XDG_CONFIG_HOME"] = folder
        app = NotepadApplication()
        app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        app.register()
        app.activate()
        window = app.window
        page = window.current()
        text = "Heading\n- [ ] First task\n- [x] Second task\n"
        page.buffer.set_text(text)
        flush()

        assert page.editor.get_accessible_role() == Gtk.AccessibleRole.TEXT_BOX
        checkboxes = [x for x in page.inline.widgets if isinstance(x, Gtk.CheckButton)]
        assert len(checkboxes) == 2
        assert all(x.get_accessible_role() == Gtk.AccessibleRole.CHECKBOX for x in checkboxes)
        assert all(x.get_focusable() for x in checkboxes)
        assert all("Space" in x.get_tooltip_text() for x in checkboxes)
        assert [x.get_active() for x in checkboxes] == [False, True]

        first = checkboxes[0]
        assert first.grab_focus()
        assert first.has_focus()
        first.activate()
        flush()
        assert first.has_focus(), "Keyboard checkbox focus must survive activation"
        assert page.note.text == text.replace("- [ ] First", "- [x] First")
        assert checkboxes[0].get_active()
        window.undo_current()
        flush()
        assert first.has_focus(), "Undo must not discard the focused control"
        assert page.note.text == text
        window.redo_current()
        flush()
        assert first.has_focus(), "Redo must preserve the focused task control"
        assert page.note.text == text.replace("- [ ] First", "- [x] First")
        window.undo_current()
        flush()
        assert first.has_focus()
        assert page.note.text == text

        # Switching to preview and back must restore focus to the editor.
        window.toggle_preview()
        assert window.preview_enabled
        window.toggle_preview()
        assert not window.preview_enabled
        assert page.editor.has_focus()
        assert page.note.text == text

        # Read-only display mode can be toggled without changing note bytes.
        window._set_live_markdown(False)
        flush()
        assert not page.inline.widgets
        assert page.note.text == text
        window._set_live_markdown(True)
        flush()
        assert len(page.inline.widgets) == 2
        assert page.note.text == text

        window._close_confirmed = True
        window.close()
        app.quit()
        print("Native GTK accessibility focus and source integrity: PASS")


if __name__ == "__main__":
    main()
