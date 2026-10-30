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
        assert page.container.has_css_class("paper-pane")
        assert window.words_status.get_text() == "0 words"
        assert window.lines_status.get_text() == "1 line"
        assert window.wrap_status.get_text() == "Wrap: On"
        page.buffer.set_text("GoreeCloud test note\nSecond line")
        assert page.note.dirty
        assert window.words_status.get_text() == "5 words"
        assert window.lines_status.get_text() == "2 lines"
        assert window.file_status.get_text() == "Unsaved changes"
        window.find_bar.show_find()
        assert window.find_bar.get_visible()
        window.find_bar.entry.set_text("nOtE")
        assert len(window.find_bar.matches) == 1
        window.find_bar.move(True)
        selected = page.buffer.get_selection_bounds()
        assert selected and page.buffer.get_text(*selected, True) == "note"
        assert page.note.dirty, "Search highlighting must not mark notes as saved"
        window.find_bar.hide_find()
        assert not window.find_bar.get_visible()
        assert not window.find_bar.matches
        path = Path(folder) / "note.txt"
        page.note.save(path)
        page.refresh_label()
        window.update_status()
        assert window.file_status.get_text() == "Saved on this device"
        window.find_bar.show_find()
        window.find_bar.entry.set_text("Second")
        assert window.find_bar.matches
        window.find_bar.hide_find()
        assert not page.note.dirty, "Find must leave saved documents clean"
        assert path.read_text() == "GoreeCloud test note\nSecond line"
        window.new_tab()
        assert len(window.pages) == 2
        second = window.current()
        second.buffer.set_text("hello HELLO hello")
        window.find_bar.show_find()
        window.find_bar.entry.set_text("hello")
        assert len(window.find_bar.matches) == 3
        window.find_bar.move(True)
        first_start = second.buffer.get_selection_bounds()[0].get_offset()
        window.find_bar.move(True)
        middle_start = second.buffer.get_selection_bounds()[0].get_offset()
        window.find_bar.move(True)
        last_start = second.buffer.get_selection_bounds()[0].get_offset()
        window.find_bar.move(True)
        wrap_start = second.buffer.get_selection_bounds()[0].get_offset()
        assert (first_start, middle_start, last_start, wrap_start) == (0, 6, 12, 0)
        second.buffer.insert(second.buffer.get_end_iter(), "!")
        assert second.note.text.endswith("!")
        window.undo_current()
        assert second.note.text == "hello HELLO hello"
        window.redo_current()
        assert second.note.text == "hello HELLO hello!"
        window.notebook.set_current_page(window.notebook.page_num(page.container))
        window.find_bar.refresh()
        assert not window.find_bar.matches
        window.find_bar.hide_find()
        # Reordering changes notebook positions, not the current document identity.
        window.notebook.reorder_child(page.container, 1)
        window.notebook.set_current_page(1)
        assert window.current() is page
        window.open_path(path)
        assert len(window.pages) == 2, "Existing file should not open twice"
        window._set_wrap(False)
        assert window.wrap_status.get_text() == "Wrap: Off"
        assert all(p.editor.get_wrap_mode() == Gtk.WrapMode.NONE for p in window.pages)
        window._set_wrap(True)
        assert window.wrap_status.get_text() == "Wrap: On"
        assert all(p.editor.get_wrap_mode() == Gtk.WrapMode.WORD_CHAR for p in window.pages)
        page.buffer.set_text("# Title\n- [x] Done")
        window.toggle_preview()
        assert window.preview_enabled
        assert page.view_stack.get_visible_child_name() == "preview"
        preview_buffer = page.preview.view.get_buffer()
        preview_text = preview_buffer.get_text(*preview_buffer.get_bounds(), True)
        assert "Title" in preview_text and "☑ Done" in preview_text
        assert "# Title" not in preview_text
        assert page.note.text == "# Title\n- [x] Done"
        assert page.preview._task_lines == {1: 1}
        page.note.save(path)
        page.refresh_label()
        window.update_status()
        GLib.timeout_add(180, lambda: (loop.quit(), GLib.SOURCE_REMOVE)[1])
        loop.run()
        view = page.preview.view
        target = view.get_buffer()
        ok, marker_iter = target.get_iter_at_line_offset(1, 0)
        assert ok
        rect = view.get_iter_location(marker_iter)
        x, y = view.buffer_to_window_coords(Gtk.TextWindowType.WIDGET, rect.x + 2, rect.y + 5)
        assert not page.preview.toggle_at(x + 80, y)
        assert page.note.text == "# Title\n- [x] Done"
        assert page.preview.toggle_at(x, y)
        assert page.note.text == "# Title\n- [ ] Done"
        assert page.note.dirty and window.file_status.get_text() == "Unsaved changes"
        assert path.read_text() == "# Title\n- [x] Done"
        window.undo_current()
        assert page.note.text == "# Title\n- [x] Done"
        assert not page.note.dirty
        window.redo_current()
        assert page.note.text == "# Title\n- [ ] Done"
        window._set_appearance("dark")
        assert window.has_css_class("dark")
        window._set_appearance("light")
        assert not window.has_css_class("dark")
        window.toggle_preview()
        assert not window.preview_enabled
        assert page.view_stack.get_visible_child_name() == "edit"
        assert page.note.text == "# Title\n- [ ] Done"
        valid, source_iter = page.buffer.get_iter_at_line_offset(1, 0)
        assert valid
        page.buffer.place_cursor(source_iter)
        assert window.toggle_current_task()
        assert page.note.text == "# Title\n- [x] Done"
        assert not page.note.dirty
        assert path.read_text() == "# Title\n- [x] Done"
        window.toggle_preview()
        third = window.new_tab()
        assert third.view_stack.get_visible_child_name() == "preview"
        window.toggle_preview()
        assert third.view_stack.get_visible_child_name() == "edit"
        window._close_confirmed = True
        window.close()
        app.quit()
        print("GTK4 smoke: PASS")


if __name__ == "__main__":
    main()
