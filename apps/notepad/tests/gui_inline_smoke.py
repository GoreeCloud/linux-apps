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


def settle(milliseconds=420):
    loop = GLib.MainLoop()
    GLib.timeout_add(milliseconds, lambda: (loop.quit(), GLib.SOURCE_REMOVE)[1])
    loop.run()


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

        # Native rule width is recomputed after shrinking and restoring the
        # window. GTK TextView overlay allocation must be explicitly queued.
        window.set_default_size(1080, 720)
        settle()
        wide_view = page.editor.get_width()
        rule = next(w for w in decorations.widgets if isinstance(w, Gtk.Separator))
        wide_rule = rule.get_width()
        assert wide_view > 900 and 700 < wide_rule < wide_view
        window.set_default_size(560, 420)
        window.set_size_request(560, 420)
        settle()
        narrow_view = page.editor.get_width()
        narrow_rule = rule.get_width()
        assert narrow_view < wide_view
        assert 120 <= narrow_rule <= narrow_view - (
            page.editor.get_left_margin() + page.editor.get_right_margin()
        ), (narrow_view, narrow_rule)
        window.set_default_size(1080, 720)
        settle()
        assert rule.get_width() > narrow_rule
        assert page.note.text == note, "Resizing must not edit Markdown source"
        # Font and wrap settings can change text geometry without a source edit.
        original_font = window.prefs.get("font_size")
        window.prefs.set("font_size", min(22, original_font + 2))
        page.update_font()
        settle()
        assert page.note.text == note
        window.prefs.set("font_size", original_font)
        page.update_font()
        window._set_wrap(False)
        settle()
        assert page.note.text == note and page.inline.widgets
        window._set_wrap(True)
        settle()
        assert page.note.text == note

        path = Path(folder) / "note.md"
        page.note.save(path)
        page.refresh_label()
        window.update_status()
        assert path.read_text() == note
        assert checks[0].get_accessible_role() == Gtk.AccessibleRole.CHECKBOX
        assert checks[0].get_focusable()
        assert checks[0].grab_focus()
        assert checks[0].has_focus(), "Checkbox must accept keyboard focus"
        # GTK native activation is the action used by keyboard accessibility.
        checks[0].activate()
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
