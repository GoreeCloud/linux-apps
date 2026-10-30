"""Native GTK4 GoreeCloud Notepad window and document actions."""

from __future__ import annotations

import re
from pathlib import Path

import gi

gi.require_version("Gtk", "4.0")
gi.require_version("Gdk", "4.0")
from gi.repository import Gdk, Gio, GLib, Gtk, Pango

from .storage import Note, Preferences
from .find import FindBar
from .preview import MarkdownPreview
from .checklists import task_marker_at_line
from .theme import install as install_theme


class NotePage:
    def __init__(self, note: Note, window: "NotepadWindow"):
        self.note = note
        self.window = window
        self.buffer = Gtk.TextBuffer()
        self.buffer.set_text(note.text)
        self.buffer.set_enable_undo(True)
        self.buffer.set_max_undo_levels(100)
        self.editor = Gtk.TextView.new_with_buffer(self.buffer)
        self.editor.add_css_class("notepad-editor")
        self.editor.set_left_margin(40)
        self.editor.set_right_margin(40)
        self.editor.set_top_margin(34)
        self.editor.set_bottom_margin(30)
        self.editor.set_hexpand(True)
        self.editor.set_vexpand(True)
        self.editor.set_wrap_mode(
            Gtk.WrapMode.WORD_CHAR if window.prefs.get("word_wrap") else Gtk.WrapMode.NONE
        )
        self.update_font()
        self.editor.set_accessible_role(Gtk.AccessibleRole.TEXT_BOX)
        self.editor.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Note editor"]
        )

        self.container = Gtk.Frame()
        self.container.add_css_class('paper-pane')
        self.container.set_margin_start(16)
        self.container.set_margin_end(16)
        self.container.set_margin_bottom(10)
        self.scroller = Gtk.ScrolledWindow()
        self.container.set_hexpand(True)
        self.container.set_vexpand(True)
        self.scroller.add_css_class("editor-pane")
        self.scroller.set_child(self.editor)
        self.preview = MarkdownPreview(self.toggle_task)
        self.update_font()
        self.view_stack = Gtk.Stack()
        self.view_stack.add_named(self.scroller, "edit")
        self.view_stack.add_named(self.preview, "preview")
        self.container.set_child(self.view_stack)

        self.tab = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=9)
        tab_icon = Gtk.Image.new_from_icon_name('text-x-generic-symbolic')
        self.tab.append(tab_icon)
        self.tab_label = Gtk.Label(xalign=0)
        self.tab_label.set_ellipsize(Pango.EllipsizeMode.END)
        self.tab_label.set_max_width_chars(24)
        self.tab.append(self.tab_label)
        close = Gtk.Button.new_from_icon_name("window-close-symbolic")
        close.add_css_class("flat")
        close.add_css_class("tab-close")
        close.set_tooltip_text("Close tab")
        close.set_accessible_role(Gtk.AccessibleRole.BUTTON)
        close.connect("clicked", lambda *_: window.close_page(self))
        self.tab.append(close)
        self.buffer.connect("changed", self._changed)
        self.buffer.connect("mark-set", self._mark_set)
        self.refresh_label()

    def toggle_task(self, source_line: int):
        marker = task_marker_at_line(self.note.text, source_line)
        if marker is None:
            return False
        column, replacement = marker
        valid, start = self.buffer.get_iter_at_line_offset(source_line, column)
        if not valid:
            return False
        end = start.copy()
        end.forward_char()
        self.buffer.begin_user_action()
        try:
            self.buffer.delete(start, end)
            self.buffer.insert(start, replacement)
        finally:
            self.buffer.end_user_action()
        return True

    def set_preview(self, enabled: bool, dark: bool):
        if enabled:
            self.preview.render(self.note.text, dark)
            self.view_stack.set_visible_child_name("preview")
        else:
            self.view_stack.set_visible_child_name("edit")

    def update_font(self):
        size = self.window.prefs.get("font_size")
        family = "monospace" if self.window.prefs.get("monospace") else "sans-serif"
        # Each editor gets its own native Pango font settings via GTK CSS.
        css = Gtk.CssProvider()
        css.load_from_data(
            f"textview.notepad-editor, textview.notepad-editor text "
            f"{{ font-family: {family}; font-size: {size}pt; }}".encode()
        )
        econtext = self.editor.get_style_context()
        if hasattr(self, "_font_provider"):
            econtext.remove_provider(self._font_provider)
        econtext.add_provider(css, Gtk.STYLE_PROVIDER_PRIORITY_USER)
        self._font_provider = css
        if hasattr(self, "preview"):
            pcss = Gtk.CssProvider()
            pcss.load_from_data(
                f"textview.notepad-preview, textview.notepad-preview text "
                f"{{ font-family: {family}; font-size: {size}pt; }}".encode()
            )
            pcontext = self.preview.view.get_style_context()
            if hasattr(self, "_preview_font_provider"):
                pcontext.remove_provider(self._preview_font_provider)
            pcontext.add_provider(pcss, Gtk.STYLE_PROVIDER_PRIORITY_USER)
            self._preview_font_provider = pcss

    def refresh_label(self):
        self.tab_label.set_text(("• " if self.note.dirty else "") + self.note.name)
        self.tab_label.set_tooltip_text(str(self.note.path) if self.note.path else "Unsaved note")

    def _changed(self, buffer):
        start, end = buffer.get_bounds()
        self.note.text = buffer.get_text(start, end, True)
        self.refresh_label()
        self.window.update_status()
        if self.window.preview_enabled:
            self.set_preview(True, self.window.has_css_class("dark"))
        if hasattr(self.window, "find_bar"):
            self.window.find_bar.refresh()

    def _mark_set(self, _buffer, _iter, mark):
        if mark.get_name() == "insert":
            self.window.update_status()


class NotepadWindow(Gtk.ApplicationWindow):
    def __init__(self, app: "NotepadApplication"):
        super().__init__(application=app, title="GoreeCloud Notepad")
        self.prefs = app.prefs
        self.pages: list[NotePage] = []
        self.preview_enabled = False
        self._close_confirmed = False
        self._closing_in_progress = False
        self._desktop_interface = None
        source = Gio.SettingsSchemaSource.get_default()
        if source and source.lookup("org.gnome.desktop.interface", True):
            self._desktop_interface = Gio.Settings.new("org.gnome.desktop.interface")
            self._desktop_interface.connect("changed::color-scheme", lambda *_: self.apply_appearance())
        self.set_default_size(1080, 720)
        self.set_size_request(560, 420)
        self.add_css_class("notepad-window")

        root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.set_child(root)
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)
        header.add_css_class("notepad-header")
        header.set_title_widget(Gtk.Box())
        identity = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        identity.add_css_class("brand-identity")
        identity.append(Gtk.Image.new_from_icon_name("text-x-generic-symbolic"))
        identity.append(Gtk.Label(label="GoreeCloud Notepad"))
        header.pack_start(identity)
        self.set_titlebar(header)
        actions = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=3)
        header.pack_end(actions)

        file_button = Gtk.MenuButton()
        file_button.set_icon_name("folder-open-symbolic")
        file_button.set_tooltip_text("File")
        file_button.update_property([Gtk.AccessibleProperty.LABEL], ["File"])
        file_button.add_css_class("header-glyph")
        actions.append(file_button)
        file_button.set_popover(self._file_popover())

        new_button = self._glyph("list-add-symbolic", "New tab", self.new_tab)
        actions.append(new_button)

        settings = Gtk.MenuButton()
        settings.set_icon_name("emblem-system-symbolic")
        settings.set_tooltip_text("Settings")
        settings.update_property([Gtk.AccessibleProperty.LABEL], ["Settings"])
        settings.add_css_class("header-glyph")
        settings.set_popover(self._settings_popover())
        actions.append(settings)

        preferences = self._glyph("preferences-desktop-font-symbolic", "Preferences", self.show_preferences)
        actions.append(preferences)
        self.preview_button = self._glyph(
            "document-print-preview-symbolic", "Preview Markdown (Ctrl+Shift+M)",
            self.toggle_preview,
        )
        actions.append(self.preview_button)

        self.notebook = Gtk.Notebook()
        self.notebook.set_scrollable(True)
        self.notebook.set_show_border(False)
        tab_add = self._glyph("list-add-symbolic", "New tab", self.new_tab)
        tab_add.add_css_class("tab-add")
        self.notebook.set_action_widget(tab_add, Gtk.PackType.END)
        self.notebook.set_hexpand(True)
        self.notebook.set_vexpand(True)
        self.notebook.connect("switch-page", lambda *_: GLib.idle_add(self._tab_switched))
        self.find_bar = FindBar(self)
        root.append(self.find_bar)
        root.append(self.notebook)

        footer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        footer.add_css_class("notepad-footer")
        footer.set_margin_start(18)
        footer.set_margin_end(18)
        left = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=6)
        bullet = Gtk.Image.new_from_icon_name("text-x-generic-symbolic")
        bullet.add_css_class("brand-dot")
        left.append(bullet)
        self.words_status = Gtk.Label(label="0 words")
        self.words_status.add_css_class("footer-label")
        left.append(self.words_status)
        left.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        self.lines_status = Gtk.Label(label="1 line")
        self.lines_status.add_css_class("footer-label")
        left.append(self.lines_status)
        self.file_status = Gtk.Label(label="Local note")
        self.file_status.add_css_class("footer-label")
        self.file_status.set_ellipsize(Pango.EllipsizeMode.END)
        # Save-state belongs at the trailing end of the status bar.
        footer.append(left)
        spacer = Gtk.Box()
        spacer.set_hexpand(True)
        footer.append(spacer)
        self.position_status = Gtk.Label(label="Ln 1, Col 1  ·  0 words")
        self.position_status.add_css_class("footer-label")
        footer.append(self.position_status)
        self.wrap_status = Gtk.Label(label='Wrap: On')
        self.wrap_status.add_css_class("footer-label")
        footer.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        footer.append(self.wrap_status)
        footer.append(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL))
        footer.append(self.file_status)
        root.append(footer)

        self.connect("close-request", self._close_request)
        self.apply_appearance()
        self.new_tab()

    def toggle_preview(self):
        if not self.preview_enabled:
            self.find_bar.hide_find()
        self.preview_enabled = not self.preview_enabled
        dark = self.has_css_class("dark")
        for page in self.pages:
            page.set_preview(self.preview_enabled, dark)
        if self.preview_enabled:
            self.preview_button.set_icon_name("document-edit-symbolic")
            self.preview_button.set_tooltip_text("Edit source (Ctrl+Shift+M)")
            self.preview_button.update_property(
                [Gtk.AccessibleProperty.LABEL], ["Edit source"]
            )
        else:
            self.preview_button.set_icon_name("document-print-preview-symbolic")
            self.preview_button.set_tooltip_text("Preview Markdown (Ctrl+Shift+M)")
            page = self.current()
            if page:
                page.editor.grab_focus()

    def _tab_switched(self):
        self.update_status()
        self.find_bar.refresh()
        return False

    def _glyph(self, icon_name, tooltip, callback):
        button = Gtk.Button.new_from_icon_name(icon_name)
        button.add_css_class("flat")
        button.add_css_class("header-glyph")
        button.set_tooltip_text(tooltip)
        button.update_property([Gtk.AccessibleProperty.LABEL], [tooltip])
        button.connect("clicked", lambda *_: callback())
        return button

    def _file_popover(self):
        pop = Gtk.Popover()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        box.set_margin_top(10)
        box.set_margin_bottom(10)
        box.set_margin_start(10)
        box.set_margin_end(10)
        actions = [
            ("New tab", "Ctrl+T", self.new_tab),
            ("Open…", "Ctrl+O", self.open_dialog),
            ("Find…", "Ctrl+F", lambda: self.find_bar.show_find()),
            ("Toggle Markdown preview", "Ctrl+Shift+M", self.toggle_preview),
            ("Toggle checklist item", "Ctrl+Enter", self.toggle_current_task),
            ("Save", "Ctrl+S", self.save_current),
            ("Save as…", "Ctrl+Shift+S", self.save_as_current),
            ("Close tab", "Ctrl+W", self.close_current),
            ("Quit", "Ctrl+Q", self.close),
        ]
        for label, shortcut, action in actions:
            button = Gtk.Button()
            button.add_css_class("flat")
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
            row.append(Gtk.Label(label=label, xalign=0, hexpand=True))
            detail = Gtk.Label(label=shortcut)
            detail.add_css_class("dim-label")
            row.append(detail)
            button.set_child(row)
            button.connect("clicked", lambda _b, callback=action: (pop.popdown(), callback()))
            box.append(button)
        pop.set_child(box)
        return pop

    def _settings_popover(self):
        pop = Gtk.Popover()
        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        box.set_margin_top(18)
        box.set_margin_bottom(18)
        box.set_margin_start(18)
        box.set_margin_end(18)
        title = Gtk.Label(label="Appearance & editing", xalign=0)
        title.add_css_class("heading")
        box.append(title)
        box.append(Gtk.Label(label="Color theme", xalign=0))
        appearance = Gtk.DropDown.new_from_strings(["Light", "Dark", "Follow system"])
        appearance.set_selected(("light", "dark", "system").index(self.prefs.get("appearance")))
        appearance.connect("notify::selected", lambda d, _p: self._set_appearance(
            ("light", "dark", "system")[d.get_selected()]
        ))
        box.append(appearance)
        row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=14)
        row.append(Gtk.Label(label="Wrap long lines", hexpand=True, xalign=0))
        switch = Gtk.Switch()
        switch.set_active(self.prefs.get("word_wrap"))
        switch.connect("notify::active", lambda s, _p: self._set_wrap(s.get_active()))
        row.append(switch)
        box.append(row)
        pop.set_child(box)
        return pop

    def _set_appearance(self, mode):
        self.prefs.set("appearance", mode)
        self.apply_appearance()

    def _system_is_dark(self):
        if self._desktop_interface is None:
            return False
        try:
            return self._desktop_interface.get_string("color-scheme") == "prefer-dark"
        except GLib.Error:
            return False

    def apply_appearance(self):
        mode = self.prefs.get("appearance")
        dark = mode == "dark" or (mode == "system" and self._system_is_dark())
        gtk_settings = Gtk.Settings.get_default()
        if gtk_settings:
            gtk_settings.set_property("gtk-application-prefer-dark-theme", dark)
        if dark:
            self.add_css_class("dark")
        else:
            self.remove_css_class("dark")
        if self.preview_enabled:
            for page in self.pages:
                page.set_preview(True, dark)

    def _set_wrap(self, enabled):
        self.prefs.set("word_wrap", bool(enabled))
        for page in self.pages:
            page.editor.set_wrap_mode(
                Gtk.WrapMode.WORD_CHAR if enabled else Gtk.WrapMode.NONE
            )
            page.preview.view.set_wrap_mode(
                Gtk.WrapMode.WORD_CHAR if enabled else Gtk.WrapMode.NONE
            )
        self.update_status()

    def show_preferences(self):
        dialog = Gtk.Window(title="Editor preferences", transient_for=self, modal=True)
        dialog.set_default_size(360, 240)
        body = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        body.set_margin_top(24)
        body.set_margin_bottom(24)
        body.set_margin_start(24)
        body.set_margin_end(24)
        title = Gtk.Label(label="Make writing your own", xalign=0)
        title.add_css_class("title-3")
        body.append(title)
        font_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        font_row.append(Gtk.Label(label="Text size", xalign=0, hexpand=True))
        size = Gtk.SpinButton.new_with_range(11, 26, 1)
        size.set_value(self.prefs.get("font_size"))
        size.connect("value-changed", lambda spin: self._set_font_size(spin.get_value_as_int()))
        font_row.append(size)
        body.append(font_row)
        mono_row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=16)
        mono_row.append(Gtk.Label(label="Monospaced text", xalign=0, hexpand=True))
        mono = Gtk.Switch()
        mono.set_active(self.prefs.get("monospace"))
        mono.connect("notify::active", lambda switch, _pspec: self._set_monospace(switch.get_active()))
        mono_row.append(mono)
        body.append(mono_row)
        done = Gtk.Button(label="Done", halign=Gtk.Align.END)
        done.add_css_class("suggested-action")
        done.connect("clicked", lambda *_: dialog.close())
        body.append(done)
        dialog.set_child(body)
        dialog.present()

    def _set_font_size(self, size):
        self.prefs.set("font_size", size)
        for page in self.pages:
            page.update_font()

    def _set_monospace(self, enabled):
        self.prefs.set("monospace", bool(enabled))
        for page in self.pages:
            page.update_font()

    def current(self) -> NotePage | None:
        index = self.notebook.get_current_page()
        widget = self.notebook.get_nth_page(index) if index >= 0 else None
        return next((page for page in self.pages if page.container == widget), None)

    def new_tab(self, note: Note | None = None):
        page = NotePage(note or Note(), self)
        self.pages.append(page)
        if self.preview_enabled:
            page.set_preview(True, self.has_css_class("dark"))
        index = self.notebook.append_page(page.container, page.tab)
        self.notebook.set_tab_reorderable(page.container, True)
        self.notebook.set_current_page(index)
        if not self.preview_enabled:
            page.editor.grab_focus()
        self.update_status()
        self.find_bar.refresh()
        return page

    def open_path(self, path: Path):
        path = Path(path)
        for page in self.pages:
            if page.note.path is not None and page.note.path.resolve() == path.resolve():
                self.notebook.set_current_page(self.notebook.page_num(page.container))
                if not self.preview_enabled:
                    page.editor.grab_focus()
                return page
        try:
            note = Note.open(path)
        except (OSError, UnicodeError) as exc:
            self._error("Could not open file", str(exc))
            return None
        if len(self.pages) == 1 and not self.pages[0].note.dirty and not self.pages[0].note.text and self.pages[0].note.path is None:
            self._remove_page(self.pages[0])
        return self.new_tab(note)

    def open_dialog(self):
        chooser = Gtk.FileDialog()
        chooser.set_title("Open a note")
        chooser.open(self, None, self._opened)

    def _opened(self, chooser, result):
        try:
            file = chooser.open_finish(result)
            if file is None:
                return
            path = file.get_path()
            if path is None:
                self._error("Choose a local file", "Remote locations are not supported.")
            else:
                self.open_path(Path(path))
        except GLib.Error as exc:
            if not exc.matches(Gtk.DialogError.quark(), Gtk.DialogError.DISMISSED):
                self._error("Could not open file", str(exc))

    def undo_current(self):
        page = self.current()
        if page and page.buffer.get_can_undo():
            page.buffer.undo()

    def redo_current(self):
        page = self.current()
        if page and page.buffer.get_can_redo():
            page.buffer.redo()

    def toggle_current_task(self):
        page = self.current()
        if page:
            line = page.buffer.get_iter_at_mark(page.buffer.get_insert()).get_line()
            return page.toggle_task(line)
        return False

    def save_current(self):
        page = self.current()
        if page:
            self._save_page(page)

    def save_as_current(self):
        page = self.current()
        if page:
            self._save_page(page, save_as=True)

    def _save_page(self, page, save_as=False, on_saved=None, on_cancel=None):
        if page.note.path is not None and not save_as:
            try:
                page.note.save()
                page.refresh_label()
                self.update_status()
                if on_saved:
                    on_saved()
            except OSError as exc:
                self._error("Could not save note", str(exc))
                if on_cancel:
                    on_cancel()
            return
        chooser = Gtk.FileDialog()
        chooser.set_title("Save note as")
        chooser.set_initial_name(page.note.name if page.note.path else "Untitled.txt")

        def finished(dialog, result):
            try:
                file = dialog.save_finish(result)
                if file is None:
                    if on_cancel:
                        on_cancel()
                    return
                path = file.get_path()
                if path is None:
                    self._error("Choose a local file", "Remote locations are not supported.")
                    if on_cancel:
                        on_cancel()
                    return
                page.note.save(Path(path))
                page.refresh_label()
                self.update_status()
                if on_saved:
                    on_saved()
            except GLib.Error as exc:
                if not exc.matches(Gtk.DialogError.quark(), Gtk.DialogError.DISMISSED):
                    self._error("Could not save note", str(exc))
                if on_cancel:
                    on_cancel()
            except OSError as exc:
                self._error("Could not save note", str(exc))
                if on_cancel:
                    on_cancel()

        chooser.save(self, None, finished)

    def _error(self, message, detail):
        alert = Gtk.AlertDialog()
        alert.set_message(message)
        alert.set_detail(detail)
        alert.set_buttons(["OK"])
        alert.choose(self, None, lambda *_: None)

    def close_current(self):
        page = self.current()
        if page:
            self.close_page(page)

    def close_page(self, page):
        self._confirm_page(page, lambda: self._after_tab_close(page))

    def _after_tab_close(self, page):
        self._remove_page(page)
        if not self.pages:
            self.new_tab()

    def _remove_page(self, page):
        index = self.notebook.page_num(page.container)
        if index >= 0:
            self.notebook.remove_page(index)
        if page in self.pages:
            self.pages.remove(page)
        self.update_status()
        self.find_bar.refresh()

    def _confirm_page(self, page, proceed, on_cancel=None):
        if not page.note.dirty:
            proceed()
            return
        alert = Gtk.AlertDialog()
        alert.set_message(f"Save changes to {page.note.name}?")
        alert.set_detail("Your changes will be lost if you discard them.")
        alert.set_buttons(["Cancel", "Discard", "Save"])
        alert.set_cancel_button(0)
        alert.set_default_button(2)

        def answered(dialog, result):
            try:
                decision = dialog.choose_finish(result)
            except GLib.Error:
                if on_cancel:
                    on_cancel()
                return
            if decision == 1:
                proceed()
            elif decision == 2:
                self._save_page(page, on_saved=proceed, on_cancel=on_cancel)
            elif on_cancel:
                on_cancel()

        alert.choose(self, None, answered)

    def _close_request(self, _window):
        if self._close_confirmed:
            return False
        if self._closing_in_progress:
            return True
        dirty_pages = [page for page in self.pages if page.note.dirty]
        if not dirty_pages:
            return False
        self._closing_in_progress = True

        def next_page(index=0):
            if index >= len(dirty_pages):
                self._close_confirmed = True
                self.close()
                return
            self._confirm_page(
                dirty_pages[index],
                lambda: next_page(index + 1),
                on_cancel=lambda: setattr(self, "_closing_in_progress", False),
            )

        next_page()
        return True

    def update_status(self):
        page = self.current()
        if not page:
            return False
        buf = page.buffer
        cursor = buf.get_iter_at_mark(buf.get_insert())
        words = len(re.findall(r"\S+", page.note.text))
        lines = page.note.text.count("\n") + 1
        self.words_status.set_text(f"{words} words" if words != 1 else "1 word")
        self.lines_status.set_text(f"{lines} lines" if lines != 1 else "1 line")
        self.position_status.set_text(
            f"Ln {cursor.get_line() + 1}, Col {cursor.get_line_offset() + 1}"
        )
        self.wrap_status.set_text("Wrap: On" if self.prefs.get("word_wrap") else "Wrap: Off")
        status = "Unsaved changes" if page.note.dirty else ("Saved on this device" if page.note.path else "Not saved yet")
        self.file_status.set_text(status)
        return False


class NotepadApplication(Gtk.Application):
    def __init__(self):
        super().__init__(
            application_id="com.goreecloud.Notepad",
            flags=Gio.ApplicationFlags.HANDLES_OPEN,
        )
        self.prefs = Preferences()
        self.window = None

    def do_startup(self):
        Gtk.Application.do_startup(self)
        install_theme()
        shortcuts = {
            "app.new": ["<Primary>t"],
            "app.open": ["<Primary>o"],
            "app.save": ["<Primary>s"],
            "app.save-as": ["<Primary><Shift>s"],
            "app.close-tab": ["<Primary>w"],
            "app.quit": ["<Primary>q"],
            "app.find": ["<Primary>f"],
            "app.find-next": ["F3"],
            "app.find-previous": ["<Shift>F3"],
            "app.next-tab": ["<Primary>Page_Down"],
            "app.previous-tab": ["<Primary>Page_Up"],
            "app.undo": ["<Primary>z"],
            "app.redo": ["<Primary><Shift>z", "<Primary>y"],
            "app.preview": ["<Primary><Shift>m"],
            "app.toggle-task": ["<Primary>Return"],
        }
        handlers = {
            "new": lambda: self.window.new_tab(),
            "open": lambda: self.window.open_dialog(),
            "save": lambda: self.window.save_current(),
            "save-as": lambda: self.window.save_as_current(),
            "close-tab": lambda: self.window.close_current(),
            "quit": lambda: self.window.close(),
            "find": lambda: self.window.find_bar.show_find(),
            "find-next": lambda: self.window.find_bar.move(True),
            "find-previous": lambda: self.window.find_bar.move(False),
            "next-tab": lambda: self.window.notebook.next_page(),
            "previous-tab": lambda: self.window.notebook.prev_page(),
            "undo": lambda: self.window.undo_current(),
            "redo": lambda: self.window.redo_current(),
            "preview": lambda: self.window.toggle_preview(),
            "toggle-task": lambda: self.window.toggle_current_task(),
        }
        for name, callback in handlers.items():
            action = Gio.SimpleAction.new(name, None)
            action.connect("activate", lambda _a, _p, cb=callback: cb())
            self.add_action(action)
        for action, keys in shortcuts.items():
            self.set_accels_for_action(action, keys)

    def do_activate(self):
        if self.window is None or not self.window.get_visible():
            self.window = NotepadWindow(self)
        self.window.present()

    def do_open(self, files, _n_files, _hint):
        self.do_activate()
        for file in files:
            path = file.get_path()
            if path is not None:
                self.window.open_path(Path(path))


def main(argv=None):
    application = NotepadApplication()
    return application.run(argv)
