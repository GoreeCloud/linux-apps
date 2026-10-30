"""Read-only native Markdown preview."""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, Pango

from .markdown import Line, Run, parse_markdown


class MarkdownPreview(Gtk.ScrolledWindow):
    MAX_CHARS = 500_000

    def __init__(self):
        super().__init__()
        self.add_css_class("editor-pane")
        self.set_hexpand(True)
        self.set_vexpand(True)
        self.view = Gtk.TextView()
        self.view.add_css_class("notepad-preview")
        self.view.set_editable(False)
        self.view.set_cursor_visible(False)
        self.view.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.view.set_left_margin(40)
        self.view.set_right_margin(40)
        self.view.set_top_margin(34)
        self.view.set_bottom_margin(30)
        self.view.update_property(
            [Gtk.AccessibleProperty.LABEL], ["Read-only Markdown preview"]
        )
        self.set_child(self.view)

    def render(self, text: str, dark: bool = False):
        """Build display-only text. Never change the editable note buffer."""
        truncated = len(text) > self.MAX_CHARS
        lines = parse_markdown(text[:self.MAX_CHARS])
        if truncated:
            lines.append(Line(
                (Run("Preview limited to the first 500,000 characters.", "warning"),),
                "quote",
            ))
        buf = Gtk.TextBuffer()
        blue = "#a6c6ff" if dark else "#2566be"
        tags = {
            "h1": {"weight": Pango.Weight.BOLD, "scale": 1.85,
                   "pixels_above_lines": 16, "pixels_below_lines": 7},
            "h2": {"weight": Pango.Weight.BOLD, "scale": 1.4,
                   "pixels_above_lines": 12, "pixels_below_lines": 5},
            "h3": {"weight": Pango.Weight.BOLD, "scale": 1.17,
                   "pixels_above_lines": 10, "pixels_below_lines": 4},
            "bold": {"weight": Pango.Weight.BOLD},
            "italic": {"style": Pango.Style.ITALIC},
            "strike": {"strikethrough": True},
            "code": {"family": "monospace",
                     "background": "#354054" if dark else "#edf2f9"},
            "link": {"foreground": blue, "underline": Pango.Underline.SINGLE},
            "quote": {"foreground": "#a6c6ff" if dark else "#6b7790"},
            "bullet": {"foreground": blue},
            "task": {"foreground": blue},
            "rule": {"foreground": "#7a86a0"},
            "warning": {"foreground": "#c77a37"},
            "list": {"pixels_above_lines": 2},
            "blank": {"pixels_above_lines": 5},
        }
        for name, props in tags.items():
            buf.create_tag(name, **props)
        for line in lines:
            first_offset = buf.get_char_count()
            for run in line.runs:
                start = buf.get_char_count()
                buf.insert(buf.get_end_iter(), run.text)
                if run.style in tags:
                    buf.apply_tag_by_name(
                        run.style, buf.get_iter_at_offset(start), buf.get_end_iter()
                    )
            buf.insert(buf.get_end_iter(), "\n")
            if line.block in tags:
                buf.apply_tag_by_name(
                    line.block, buf.get_iter_at_offset(first_offset), buf.get_end_iter()
                )
        self.view.set_buffer(buf)
