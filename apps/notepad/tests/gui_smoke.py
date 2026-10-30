"""Run with xvfb-run, after GTK4 and PyGObject have been installed."""

import tempfile
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import GLib, Gtk

from goreecloud_notepad.app import NotepadApplication


def main():
    with tempfile.TemporaryDirectory() as folder:
        app = NotepadApplication()
        app.register()
        app.activate()
        window = app.window
        assert window is not None, "App window missing"
        assert window.get_titlebar().get_show_title_buttons()
        page = window.current()
        assert page.editor.get_wrap_mode() == Gtk.WrapMode.WORD_CHAR
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
