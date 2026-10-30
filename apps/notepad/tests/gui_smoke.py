"""Run with xvfb-run, after GTK4 and PyGObject have been installed."""

import os
import sys
import tempfile
from pathlib import Path

# Make the app importable when executed directly by CI.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gio, GLib, Gtk

from goreecloud_notepad.app import NotepadApplication
from goreecloud_notepad.theme import STYLESHEET


def main():
    css_errors = []
    provider = Gtk.CssProvider()
    provider.connect("parsing-error", lambda _provider, _section, error: css_errors.append(str(error)))
    provider.load_from_data(STYLESHEET.encode("utf-8"))
    assert not css_errors, f"Invalid GTK styling: {css_errors}"
    with tempfile.TemporaryDirectory() as folder:
        os.environ["XDG_CONFIG_HOME"] = folder
        app = NotepadApplication()
        # Avoid activating a running desktop instance during isolated smoke tests.
        app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
        app.register()
        app.activate()
        window = app.window
        assert window is not None, "App window missing"
        assert window.get_titlebar().get_show_title_buttons()
        page = window.current()
        assert page.editor.get_wrap_mode() == Gtk.WrapMode.WORD_CHAR
        loop = GLib.MainLoop()
        GLib.timeout_add(250, lambda: (loop.quit(), GLib.SOURCE_REMOVE)[1])
        loop.run()
        header = window.notebook.get_first_child()
        while header and header.get_css_name() != "header":
            header = header.get_next_sibling()
        assert header is not None, "Notebook header is missing"
        tab_height = header.get_height()
        assert 0 < tab_height <= 48, f"Tab strip is too tall: {tab_height}px"
        print(f"Native tab strip: {tab_height}px")
        page.buffer.set_text("GoreeCloud test note")
        assert page.note.dirty
        path = Path(folder) / "note.txt"
        page.note.save(path)
        page.refresh_label()
        assert path.read_text() == "GoreeCloud test note"
        window.new_tab()
        assert len(window.pages) == 2
        window.open_path(path)
        assert len(window.pages) == 2, "Existing file should not open twice"
        window._set_wrap(False)
        assert all(p.editor.get_wrap_mode() == Gtk.WrapMode.NONE for p in window.pages)
        window._set_wrap(True)
        assert all(p.editor.get_wrap_mode() == Gtk.WrapMode.WORD_CHAR for p in window.pages)
        window._set_appearance("dark")
        assert window.has_css_class("dark")
        window._set_appearance("light")
        assert not window.has_css_class("dark")
        window._close_confirmed = True
        window.close()
        app.quit()
        print("GTK4 smoke: PASS")


if __name__ == "__main__":
    main()
