"""Native GTK4 regression for checkbox line indexing."""
import os
import sys
import tempfile
from pathlib import Path
import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from goreecloud_notepad.app import NotepadApplication


def flush():
    context = GLib.MainContext.default()
    for _ in range(90):
        if not context.pending():
            break
        context.iteration(False)


def main():
    with tempfile.TemporaryDirectory(prefix="gcn-gtk-lines-") as folder:
        os.environ["XDG_CONFIG_HOME"] = folder
        app = NotepadApplication()
        app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        app.register()
        app.activate()
        window = app.window
        page = window.current()
        raw = "Heading" + chr(8232) + "- [ ] Visual\n- [ ] Task\n"
        page.buffer.set_text(raw)
        flush()
        checks = [w for w in page.inline.widgets if isinstance(w, Gtk.CheckButton)]
        assert len(checks) == 1 and checks[0]._source_line == 1
        checks[0].activate()
        flush()
        assert page.note.text == raw.replace('- [ ] Task', '- [x] Task')
        window.undo_current()
        assert page.note.text == raw
        for ending in ('\n', '\r', '\r\n', chr(8233)):
            source = '- [ ] First' + ending + '- [ ] Second\n'
            page.buffer.set_text(source)
            flush()
            controls = [w for w in page.inline.widgets if isinstance(w, Gtk.CheckButton)]
            assert len(controls) == 2
            controls[1].activate()
            flush()
            assert page.note.text == source.replace('- [ ] Second', '- [x] Second')
            window.undo_current()
            assert page.note.text == source
        window._close_confirmed = True
        window.close()
        app.quit()
        print('GTK Unicode source-line smoke: PASS')


if __name__ == '__main__':
    main()
