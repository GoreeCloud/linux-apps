"""GTK4 acceptance test: source tags must not alter data or undo history."""
import os
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib

from goreecloud_notepad.app import NotepadApplication


def tick():
    loop = GLib.MainLoop()
    GLib.timeout_add(120, lambda: (loop.quit(), GLib.SOURCE_REMOVE)[1])
    loop.run()


def wait_for(condition):
    loop = GLib.MainLoop()
    attempts = [0]
    def check():
        attempts[0] += 1
        if condition() or attempts[0] >= 80:
            loop.quit()
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE
    GLib.timeout_add(25, check)
    loop.run()
    assert condition(), "Timed out waiting for GTK styling update"


def main():
    with tempfile.TemporaryDirectory(prefix="notepad-style-test-") as folder:
        os.environ["XDG_CONFIG_HOME"] = folder
        app = NotepadApplication()
        app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        app.register()
        app.activate()
        window = app.window
        page = window.current()
        text = "# Plans\nUse **bold**, *italic*, and `code`.\n- [x] Complete"
        page.buffer.set_text(text)
        path = Path(folder) / "plan.md"
        page.note.save(path)
        page.refresh_label()
        window.update_status()
        before_undo = page.buffer.get_can_undo()
        bold_tag = page.styling.tags["bold"]
        wait_for(lambda: page.buffer.get_iter_at_offset(text.index("bold")).has_tag(bold_tag))
        assert not page.note.dirty, "Styling must not mark saved notes dirty"
        assert path.read_text() == text
        assert page.note.text == text
        assert page.buffer.get_can_undo() == before_undo
        bold_start = page.buffer.get_iter_at_offset(text.index("bold"))
        assert bold_start.has_tag(bold_tag), "Markdown content should be bold"
        marker = page.buffer.get_iter_at_offset(text.index("**"))
        assert marker.has_tag(page.styling.tags["marker"])

        page.buffer.select_range(
            page.buffer.get_iter_at_offset(text.index("italic")),
            page.buffer.get_iter_at_offset(text.index("italic") + len("italic")),
        )
        page.styling.refresh()
        bounds = page.buffer.get_selection_bounds()
        assert bounds and page.buffer.get_text(*bounds, True) == "italic"
        window._set_appearance("dark")
        tick()
        assert page.styling.dark
        assert not page.note.dirty

        window._set_live_markdown(False)
        wait_for(lambda: not page.buffer.get_iter_at_offset(text.index("bold")).has_tag(bold_tag))
        assert not page.buffer.get_iter_at_offset(text.index("bold")).has_tag(bold_tag)
        assert not page.note.dirty
        assert path.read_text() == text
        window._set_live_markdown(True)
        wait_for(lambda: page.buffer.get_iter_at_offset(text.index("bold")).has_tag(bold_tag))
        assert page.buffer.get_iter_at_offset(text.index("bold")).has_tag(bold_tag)
        assert not page.note.dirty

        window.find_bar.show_find()
        window.find_bar.entry.set_text("bold")
        assert window.find_bar.matches
        search_tag = page.buffer.get_tag_table().lookup("goreecloud-find")
        assert page.buffer.get_iter_at_offset(text.index("bold")).has_tag(search_tag)
        page.styling.refresh()
        assert page.buffer.get_iter_at_offset(text.index("bold")).has_tag(search_tag)
        window.find_bar.hide_find()

        # A real formatting edit still creates normal undo history.
        page.buffer.select_range(
            page.buffer.get_iter_at_offset(text.index("Complete")),
            page.buffer.get_iter_at_offset(text.index("Complete") + len("Complete")),
        )
        window.format_current("bold")
        assert page.note.dirty
        assert path.read_text() == text
        tick()
        window.undo_current()
        tick()
        assert page.note.text == text
        assert not page.note.dirty
        window.redo_current()
        tick()
        assert page.note.dirty
        window._close_confirmed = True
        window.close()
        app.quit()
    print("GTK4 live Markdown source styling: PASS")


if __name__ == "__main__":
    main()
