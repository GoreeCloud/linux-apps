"""Native GTK4 in-note search; no disk or network access.

Search runs against the active Gtk.TextBuffer.  Highlight tags never change the
document text or its saved/dirty state.
"""

from __future__ import annotations

import gi

gi.require_version("Gtk", "4.0")
from gi.repository import Gdk, Gtk


class FindBar(Gtk.Box):
    """Compact search surface with wraparound next/previous navigation."""

    MAX_HIGHLIGHTS = 500

    def __init__(self, window):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.window = window
        self.matches: list[tuple[int, int]] = []
        self._matched_page = None
        self.add_css_class("notepad-findbar")
        self.set_margin_start(18)
        self.set_margin_end(18)
        self.set_margin_top(2)
        self.set_margin_bottom(6)
        self.set_visible(False)

        self.entry = Gtk.SearchEntry()
        self.entry.set_placeholder_text("Find in current note")
        self.entry.set_hexpand(True)
        self.entry.set_width_chars(24)
        self.entry.set_tooltip_text("Find text (Ctrl+F)")
        self.entry.connect("changed", lambda *_: self.refresh())
        self.entry.connect("activate", lambda *_: self.move(True))
        key = Gtk.EventControllerKey()
        key.connect("key-pressed", self._key_pressed)
        self.entry.add_controller(key)
        self.append(self.entry)

        self.count = Gtk.Label(label="")
        self.count.add_css_class("footer-label")
        self.count.set_width_chars(14)
        self.append(self.count)

        self.previous = self._icon("go-up-symbolic", "Previous match (Shift+F3)", lambda: self.move(False))
        self.next = self._icon("go-down-symbolic", "Next match (F3)", lambda: self.move(True))
        self.close_button = self._icon("window-close-symbolic", "Close search (Esc)", self.hide_find)
        self.append(self.previous)
        self.append(self.next)
        self.append(self.close_button)

    @staticmethod
    def _icon(name, tooltip, callback):
        button = Gtk.Button.new_from_icon_name(name)
        button.add_css_class("flat")
        button.add_css_class("find-glyph")
        button.set_tooltip_text(tooltip)
        button.update_property([Gtk.AccessibleProperty.LABEL], [tooltip])
        button.connect("clicked", lambda *_: callback())
        return button

    def _key_pressed(self, _controller, keyval, _keycode, state):
        if keyval == Gdk.KEY_Escape:
            self.hide_find()
            return True
        if keyval in (Gdk.KEY_Return, Gdk.KEY_KP_Enter) and state & Gdk.ModifierType.SHIFT_MASK:
            self.move(False)
            return True
        return False

    def show_find(self):
        self.set_visible(True)
        page = self.window.current()
        if page is not None:
            bounds = page.buffer.get_selection_bounds()
            if bounds:
                start, end = bounds
                text = page.buffer.get_text(start, end, True)
                if 0 < len(text) <= 128 and "\n" not in text and "\r" not in text:
                    self.entry.set_text(text)
        self.refresh()
        self.entry.grab_focus()
        self.entry.select_region(0, -1)

    def hide_find(self):
        self.set_visible(False)
        self._clear_all()
        page = self.window.current()
        if page is not None:
            page.editor.grab_focus()

    def _clear_all(self):
        for page in self.window.pages:
            tag = page.buffer.get_tag_table().lookup("goreecloud-find")
            if tag is not None:
                start, end = page.buffer.get_bounds()
                page.buffer.remove_tag(tag, start, end)
        self.matches = []
        self._matched_page = None

    @staticmethod
    def _tag(page):
        tag = page.buffer.get_tag_table().lookup("goreecloud-find")
        if tag is None:
            tag = page.buffer.create_tag(
                "goreecloud-find", background="#bad4ff", foreground="#183a6e"
            )
        return tag

    def refresh(self):
        self._clear_all()
        if not self.get_visible():
            self.count.set_text("")
            return
        page = self.window.current()
        query = self.entry.get_text()
        if page is None or not query:
            self.count.set_text("Type to search")
            self.previous.set_sensitive(False)
            self.next.set_sensitive(False)
            return

        self._matched_page = page
        cursor = page.buffer.get_start_iter()
        tag = self._tag(page)
        flags = Gtk.TextSearchFlags.CASE_INSENSITIVE
        while len(self.matches) < self.MAX_HIGHLIGHTS:
            found = cursor.forward_search(query, flags, None)
            if not found:
                break
            start, end = found
            self.matches.append((start.get_offset(), end.get_offset()))
            page.buffer.apply_tag(tag, start, end)
            cursor = end
        n = len(self.matches)
        self.count.set_text(
            f"{n}+ matches" if n == self.MAX_HIGHLIGHTS
            else (f"{n} match" if n == 1 else f"{n} matches")
        )
        self.previous.set_sensitive(bool(n))
        self.next.set_sensitive(bool(n))

    def move(self, forward: bool):
        if not self.get_visible():
            self.show_find()
        page = self.window.current()
        if page is None:
            return
        if page is not self._matched_page:
            self.refresh()
        if not self.matches:
            return
        bounds = page.buffer.get_selection_bounds()
        if bounds:
            sel_start, sel_end = bounds
            position = sel_end.get_offset() if forward else sel_start.get_offset()
        else:
            position = page.buffer.get_iter_at_mark(page.buffer.get_insert()).get_offset()
        if forward:
            choice = next((i for i, (start, _) in enumerate(self.matches) if start >= position), 0)
        else:
            choice = next(
                (i for i in range(len(self.matches) - 1, -1, -1)
                 if self.matches[i][0] < position),
                len(self.matches) - 1,
            )
        start_offset, end_offset = self.matches[choice]
        start = page.buffer.get_iter_at_offset(start_offset)
        end = page.buffer.get_iter_at_offset(end_offset)
        page.buffer.select_range(start, end)
        page.editor.scroll_to_mark(page.buffer.get_insert(), 0.1, True, 0.0, 0.5)
        n = len(self.matches)
        self.count.set_text(f"{choice + 1} of {n}" + ("+" if n == self.MAX_HIGHLIGHTS else ""))
        # Text selection maintains the navigation position.
