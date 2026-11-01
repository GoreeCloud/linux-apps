"""Safe native inline checklist and rule visuals over editable Markdown source.

GTK TextView overlays never insert anchors, replace source bytes, or modify saved
text. The original marker characters remain in the buffer and are only
colored to match the editor canvas while the feature is enabled.
"""
from __future__ import annotations

from gi.repository import GLib, Gtk

from .markdown import FENCE, RULE, TASK


class InlineDecorations:
    MAX_CHARS = 100_000
    MAX_WIDGETS = 350

    def __init__(self, view: Gtk.TextView, buffer: Gtk.TextBuffer, on_toggle,
                 *, dark=False, enabled=True):
        self.view = view
        self.buffer = buffer
        self.on_toggle = on_toggle
        self.dark = bool(dark)
        self.enabled = bool(enabled)
        self.widgets = []
        self._check_pool = []
        self._rule_pool = []
        self._check_index = 0
        self._rule_index = 0
        self._queued = False
        self._clearing = False
        # Tags affect paint, not text contents, offsets, or editability.
        self.marker_tag = buffer.create_tag("goreecloud-inline-marker")
        self.checked_tag = buffer.create_tag(
            "goreecloud-inline-checked", strikethrough=True,
        )
        self.set_dark(dark, refresh=False)
        self.view.connect("map", lambda *_: self.schedule())
        self.schedule()

    def set_dark(self, dark: bool, *, refresh=True):
        self.dark = bool(dark)
        self.marker_tag.set_property(
            "foreground", "#19253b" if self.dark else "#ffffff",
        )
        if refresh:
            self.schedule()

    def set_enabled(self, enabled: bool):
        self.enabled = bool(enabled)
        self.schedule()

    def schedule(self):
        if not self._queued:
            self._queued = True
            GLib.idle_add(self.refresh, priority=GLib.PRIORITY_DEFAULT_IDLE)

    def _clear(self):
        # GTK wraps TextView overlays in private GtkTextViewChild containers.
        # Reuse and hide overlays rather than removing their internal wrapper:
        # removal while a checkbox toggles can recursively dispatch events.
        for child in self.widgets:
            child.set_visible(False)
        self.widgets.clear()
        self._check_index = 0
        self._rule_index = 0
        start, end = self.buffer.get_bounds()
        self.buffer.remove_tag(self.marker_tag, start, end)
        self.buffer.remove_tag(self.checked_tag, start, end)

    def refresh(self):
        self._queued = False
        self._clear()
        if not self.enabled:
            return GLib.SOURCE_REMOVE
        start, end = self.buffer.get_bounds()
        text = self.buffer.get_text(start, end, True)
        if len(text) > self.MAX_CHARS:
            return GLib.SOURCE_REMOVE
        in_fence = False
        for line_number, source in enumerate(text.splitlines()):
            if FENCE.match(source):
                in_fence = not in_fence
                continue
            if in_fence:
                continue
            task = TASK.match(source)
            rule = RULE.match(source)
            if not task and not rule:
                continue
            if len(self.widgets) >= self.MAX_WIDGETS:
                break
            if task:
                self._task(line_number, source, task)
            elif rule:
                self._rule(line_number, source)
        return GLib.SOURCE_REMOVE

    def _iter(self, line, column):
        valid, position = self.buffer.get_iter_at_line_offset(line, column)
        return position if valid else None

    def _paint_marker(self, line, first, last):
        begin, finish = self._iter(line, first), self._iter(line, last)
        if begin is not None and finish is not None:
            self.buffer.apply_tag(self.marker_tag, begin, finish)
        return begin

    def _task(self, line, source, match):
        # The actual Markdown marker remains in the buffer for lossless saves,
        # cursor offsets, search, undo/redo, and assistive text inspection.
        body_start = match.start(2)
        begin = self._paint_marker(line, 0, body_start)
        if begin is None:
            return
        if match.group(1).lower() == "x":
            finish = self._iter(line, len(source))
            if finish is not None and body_start < len(source):
                self.buffer.apply_tag(
                    self.checked_tag, self._iter(line, body_start), finish,
                )
        is_new = self._check_index >= len(self._check_pool)
        if is_new:
            checkbox = Gtk.CheckButton()
            checkbox.add_css_class("inline-task-check")
            checkbox.set_tooltip_text("Toggle task completion")
            checkbox.connect("toggled", self._toggle_widget)
            self._check_pool.append(checkbox)
        else:
            checkbox = self._check_pool[self._check_index]
        self._check_index += 1
        checkbox._source_line = line
        self._clearing = True
        try:
            checkbox.set_active(match.group(1).lower() == "x")
        finally:
            self._clearing = False
        checkbox.update_property(
            [Gtk.AccessibleProperty.LABEL],
            [f"Mark task {'incomplete' if checkbox.get_active() else 'complete'}: "
             f"{match.group(2)[:72]}"],
        )
        rect = self.view.get_iter_location(begin)
        xpos, ypos = max(0, rect.x - 2), max(0, rect.y - 3)
        if is_new:
            self.view.add_overlay(checkbox, xpos, ypos)
        else:
            self.view.move_overlay(checkbox, xpos, ypos)
        checkbox.set_visible(True)
        self.widgets.append(checkbox)

    def _toggle_widget(self, button):
        if not self._clearing:
            self.on_toggle(button._source_line)

    def _rule(self, line, source):
        begin = self._paint_marker(line, 0, len(source))
        if begin is None:
            return
        is_new = self._rule_index >= len(self._rule_pool)
        if is_new:
            separator = Gtk.Separator(orientation=Gtk.Orientation.HORIZONTAL)
            separator.add_css_class("inline-rule")
            separator.set_can_focus(False)
            self._rule_pool.append(separator)
        else:
            separator = self._rule_pool[self._rule_index]
        self._rule_index += 1
        available = self.view.get_width() - (
            self.view.get_left_margin() + self.view.get_right_margin() + 12
        )
        separator.set_size_request(max(120, available), 1)
        rect = self.view.get_iter_location(begin)
        if is_new:
            self.view.add_overlay(separator, rect.x, rect.y + max(1, rect.height // 2))
        else:
            self.view.move_overlay(separator, rect.x, rect.y + max(1, rect.height // 2))
        separator.set_visible(True)
        self.widgets.append(separator)
