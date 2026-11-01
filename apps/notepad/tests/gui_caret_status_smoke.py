"""GTK4 line-count, caret, selection and checkbox source-integrity smoke."""
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
    ctx = GLib.MainContext.default()
    for _ in range(120):
        if not ctx.pending():
            break
        ctx.iteration(False)


def main():
    with tempfile.TemporaryDirectory(prefix="gcn-caret-") as root:
        os.environ["XDG_CONFIG_HOME"] = root
        app = NotepadApplication()
        app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        app.register()
        app.activate()
        window = app.window
        page = window.current()

        # Count logical source lines exactly as GTK does, across mixed endings.
        note = "Heading\u2029- [ ] First\r\n- [ ] Second\rThird\n"
        page.buffer.set_text(note)
        flush()
        count = page.buffer.get_line_count()
        assert count == 5, count
        assert window.lines_status.get_text() == "5 lines", (
            count, window.lines_status.get_text()
        )

        # Selection in another line must not be replaced or collapsed by
        # activating an inline task on the earlier line.
        begin = note.index("Third")
        first = page.buffer.get_iter_at_offset(begin)
        last = page.buffer.get_iter_at_offset(begin + 5)
        page.buffer.select_range(first, last)
        flush()
        selection = page.buffer.get_selection_bounds()
        assert selection and page.buffer.get_text(*selection, True) == "Third"
        assert window.position_status.get_text().startswith("Ln 4,")

        widgets = [
            child for child in page.inline.widgets
            if isinstance(child, Gtk.CheckButton)
        ]
        assert len(widgets) == 2, len(widgets)
        assert [x._source_line for x in widgets] == [1, 2]
        assert widgets[0].get_accessible_role() == Gtk.AccessibleRole.CHECKBOX
        assert widgets[0].get_focusable()
        widgets[0].activate()
        flush()
        assert page.note.text == note.replace("- [ ] First", "- [x] First")
        selection = page.buffer.get_selection_bounds()
        assert selection and page.buffer.get_text(*selection, True) == "Third"
        assert page.buffer.get_iter_at_mark(page.buffer.get_insert()).get_line() == 3
        assert window.lines_status.get_text() == "5 lines"
        window.undo_current()
        flush()
        assert page.note.text == note

        # Other separators that Python.splitlines treats as new lines must
        # not fabricate a GTK cursor location.
        page.buffer.set_text("One\u2028Two\vThree\rFour")
        flush()
        assert page.buffer.get_line_count() == 2
        assert window.lines_status.get_text() == "2 lines"
        at = page.buffer.get_iter_at_offset(len("One\u2028Two\vThree\r"))
        page.buffer.place_cursor(at)
        assert window.position_status.get_text() == "Ln 2, Col 1"

        window._close_confirmed = True
        window.close()
        app.quit()
        print("GTK line count, cursor and selection smoke: PASS")


if __name__ == "__main__":
    main()
