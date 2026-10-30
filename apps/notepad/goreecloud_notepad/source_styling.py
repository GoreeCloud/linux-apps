"""Native GTK4 Markdown formatting cues; text is never rewritten."""
from __future__ import annotations

from gi.repository import GLib, Gtk, Pango

from .source_spans import source_spans


class SourceStyling:
    """Decorate the editable source buffer without affecting file contents."""

    def __init__(self, buffer: Gtk.TextBuffer, *, dark=False, enabled=True):
        self.buffer = buffer
        self.enabled = bool(enabled)
        self.dark = bool(dark)
        self._queued = False
        self._rendering = False
        styles = {
            "h1": {"weight": Pango.Weight.BOLD, "scale": 1.55},
            "h2": {"weight": Pango.Weight.BOLD, "scale": 1.32},
            "h3": {"weight": Pango.Weight.BOLD, "scale": 1.14},
            "bold": {"weight": Pango.Weight.BOLD},
            "italic": {"style": Pango.Style.ITALIC},
            "strike": {"strikethrough": True},
            "code": {"family": "monospace"},
            "marker": {},
            "list": {"weight": Pango.Weight.BOLD},
            "task": {"weight": Pango.Weight.BOLD},
            "quote": {"style": Pango.Style.ITALIC},
            "link": {"underline": Pango.Underline.SINGLE},
        }
        self.tags = {
            style: buffer.create_tag("goreecloud-source-" + style, **properties)
            for style, properties in styles.items()
        }
        self.set_dark(dark, refresh=False)
        self.refresh()

    def set_dark(self, dark: bool, *, refresh=True):
        self.dark = bool(dark)
        colors = {
            "marker": "#9daac0" if dark else "#8190a7",
            "list": "#a6c6ff" if dark else "#2566be",
            "task": "#a6c6ff" if dark else "#2566be",
            "quote": "#b0bcd5" if dark else "#677994",
            "link": "#a6c6ff" if dark else "#2259ad",
        }
        for style, color in colors.items():
            self.tags[style].set_property("foreground", color)
        self.tags["code"].set_property(
            "background", "#354054" if dark else "#edf2f9"
        )
        if refresh:
            self.schedule()

    def set_enabled(self, enabled: bool):
        self.enabled = bool(enabled)
        self.schedule()

    def schedule(self):
        if not self._queued and not self._rendering:
            self._queued = True
            GLib.idle_add(self._run, priority=GLib.PRIORITY_DEFAULT_IDLE)

    def _run(self):
        self._queued = False
        self.refresh()
        return GLib.SOURCE_REMOVE

    def refresh(self):
        if self._rendering:
            return
        self._rendering = True
        try:
            begin, end = self.buffer.get_bounds()
            for tag in self.tags.values():
                self.buffer.remove_tag(tag, begin, end)
            if not self.enabled:
                return
            text = self.buffer.get_text(begin, end, True)
            for span in source_spans(text):
                self.buffer.apply_tag(
                    self.tags[span.style],
                    self.buffer.get_iter_at_offset(span.start),
                    self.buffer.get_iter_at_offset(span.end),
                )
        finally:
            self._rendering = False
