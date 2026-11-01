"""Performance and source-safety regression for native inline Markdown editing.

Run under Xvfb. Assertions are semantic: redraws are skipped only where the
existing GTK controls cannot be affected by the edit. Wall-time is informative
rather than a flaky CI threshold.
"""
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
    for _ in range(150):
        if not context.pending():
            return
        context.iteration(False)


def main():
    with tempfile.TemporaryDirectory(prefix="gcn-inline-perf-") as directory:
        os.environ["XDG_CONFIG_HOME"] = directory
        app = NotepadApplication()
        app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        app.register()
        app.activate()
        window = app.window
        page = window.current()
        inline = page.inline
        original_refresh = inline.refresh
        refreshes = [0]

        def counted_refresh():
            refreshes[0] += 1
            return original_refresh()

        inline.refresh = counted_refresh

        # A normal body edit after the last checkbox cannot change the
        # geometry, state or text of any existing inline control.
        note = "\n".join(f"- [ ] Task {i}" for i in range(40)) + "\nPlain paragraph\n"
        page.buffer.set_text(note)
        flush()
        assert len(inline.widgets) == 40
        assert inline._last_visual_terminated
        old_controls = list(inline.widgets)
        refreshes[0] = 0
        for _ in range(8):
            page.buffer.insert(page.buffer.get_end_iter(), "x")
            flush()
        assert refreshes[0] == 0, "Body typing should not rebuild 40 unrelated controls"
        assert old_controls == inline.widgets
        assert page.note.text == note + "x" * 8

        # Syntax after the last control must create a new control.
        page.buffer.insert(page.buffer.get_end_iter(), "\n- [ ] New task\n")
        flush()
        assert refreshes[0] >= 1
        assert len(inline.widgets) == 41

        # Editing the last task itself requires refreshing its accessible label.
        refreshes[0] = 0
        page.buffer.set_text("- [ ] Last task")
        flush()
        refreshes[0] = 0
        page.buffer.insert(page.buffer.get_end_iter(), " updated")
        flush()
        assert refreshes[0] >= 1
        assert len(inline.widgets) == 1

        # Editing text within the original controls must not use the fast path.
        page.buffer.set_text(note)
        flush()
        refreshes[0] = 0
        _, second_line = page.buffer.get_iter_at_line(1)
        page.buffer.insert(second_line, "prefix ")
        flush()
        assert refreshes[0] >= 1
        assert page.note.text.startswith("- [ ] Task 0\nprefix - [ ] Task 1")
        assert len(inline.widgets) == 39

        # At the 350-widget cap, edits after the last rendered task cannot
        # create new widgets; the entire 350 controls remain unchanged.
        capped = "\n".join(f"- [ ] Task {i}" for i in range(350)) + "\nTail\n"
        page.buffer.set_text(capped)
        flush()
        assert len(inline.widgets) == 350
        refreshes[0] = 0
        for _ in range(10):
            page.buffer.insert(page.buffer.get_end_iter(), "z")
            flush()
        assert refreshes[0] == 0
        assert page.note.text == capped + "z" * 10

        # Crossing the 100k threshold must hide all controls, then restore
        # them if the text shrinks. No second oversized copy is retained.
        page.buffer.set_text("- [ ] Task\n" + ("x" * 100 + "\n") * 1000)
        flush()
        assert not inline.widgets
        assert inline._rendered_text is None
        refreshes[0] = 0
        page.buffer.insert(page.buffer.get_end_iter(), "y")
        flush()
        assert refreshes[0] == 0
        assert inline._rendered_text is None
        page.buffer.set_text("- [ ] Task\n")
        flush()
        assert len(inline.widgets) == 1

        # Preserve source selection and original Markdown through refreshes.
        page.buffer.select_range(page.buffer.get_start_iter(), page.buffer.get_end_iter())
        start, end = page.buffer.get_selection_bounds()
        text = page.buffer.get_text(start, end, True)
        page.inline.schedule()
        flush()
        start, end = page.buffer.get_selection_bounds()
        assert page.buffer.get_text(start, end, True) == text
        assert page.note.text == text

        window._close_confirmed = True
        window.close()
        app.quit()
        print("Native inline Markdown performance / integrity smoke: PASS")


if __name__ == "__main__":
    main()
