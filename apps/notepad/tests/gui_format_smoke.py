"""GTK4 integration smoke for undoable Markdown source formatting."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, Gtk

from goreecloud_notepad.app import NotepadApplication


def main():
    with tempfile.TemporaryDirectory(prefix="notepad-format-smoke-") as folder:
        os.environ["XDG_CONFIG_HOME"] = folder
        app = NotepadApplication()
        app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        app.register()
        app.activate()
        window = app.window
        page = window.current()
        page.buffer.set_text("alpha beta gamma")
        page.buffer.select_range(
            page.buffer.get_iter_at_offset(6), page.buffer.get_iter_at_offset(10)
        )
        window.format_current("bold")
        assert page.note.text == "alpha **beta** gamma"
        selection = page.buffer.get_selection_bounds()
        assert selection and page.buffer.get_text(*selection, True) == "beta"
        window.format_current("bold")
        assert page.note.text == "alpha beta gamma"
        window.undo_current()
        assert page.note.text == "alpha **beta** gamma"
        window.redo_current()
        assert page.note.text == "alpha beta gamma"
        page.buffer.place_cursor(page.buffer.get_end_iter())
        window.format_current("italic")
        assert page.note.text == "alpha beta gamma**"
        assert page.buffer.get_iter_at_mark(page.buffer.get_insert()).get_offset() == len(
            "alpha beta gamma*"
        )
        window.undo_current()
        assert page.note.text == "alpha beta gamma"
        window.toggle_preview()
        assert window.preview_enabled
        window.format_current("code")
        assert not window.preview_enabled
        assert page.note.text == "alpha beta gamma``"
        assert all(app.lookup_action("format-" + style) for style in (
            "bold", "italic", "code", "strike"
        ))
        # Keep multiple Redo steps available until the next actual edit.
        page.buffer.set_text("one two")
        page.buffer.select_range(
            page.buffer.get_iter_at_offset(0), page.buffer.get_iter_at_offset(3)
        )
        window.format_current("bold")
        assert page.note.text == "**one** two"
        page.buffer.select_range(
            page.buffer.get_iter_at_offset(8), page.buffer.get_iter_at_offset(11)
        )
        window.format_current("bold")
        assert page.note.text == "**one** **two**"
        window.undo_current()
        assert page.note.text == "**one** two"
        window.undo_current()
        assert page.note.text == "one two"
        window.redo_current()
        assert page.note.text == "**one** two"
        assert page.buffer.get_can_redo(), "Redo must retain the next step"
        window.redo_current()
        assert page.note.text == "**one** **two**"
        window.undo_current()
        window.undo_current()
        window.redo_current()
        assert page.buffer.get_can_redo()
        page.buffer.place_cursor(page.buffer.get_end_iter())
        window.format_current("italic")
        assert page.note.text == "**one** two**"
        assert not page.buffer.get_can_redo(), "A new edit replaces redo history"
        window.undo_current()
        assert page.note.text == "**one** two"
        window.undo_current()
        assert page.note.text == "one two"
        window._close_confirmed = True
        window.close()
        app.quit()
    print("GTK4 Markdown formatting smoke: PASS")


if __name__ == "__main__":
    main()
