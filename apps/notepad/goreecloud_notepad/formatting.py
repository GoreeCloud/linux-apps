"""Pure, reversible Markdown source edits for native writing shortcuts.

Formatting never renders HTML, launches programs, or touches files. Coordinates
are Python string-character offsets (the same offsets Gtk.TextBuffer uses).
"""
from __future__ import annotations
from dataclasses import dataclass
import re


MARKERS = {"bold": "**", "italic": "*", "code": "`", "strike": "~~"}


@dataclass(frozen=True)
class MarkdownEdit:
    start: int
    end: int
    replacement: str
    selection_start: int
    selection_end: int


def inline_format(text: str, start: int, end: int, style: str) -> MarkdownEdit | None:
    """Wrap/unwrap a single-line selection, or insert paired markers at cursor.

    Selection offsets always select user content (not markup). Returns None
    for cross-line selection to avoid silently malformed Markdown.
    """
    if style not in MARKERS:
        raise ValueError(f"Unknown Markdown style: {style}")
    if not 0 <= start <= end <= len(text):
        raise ValueError("Invalid selection range")
    marker = MARKERS[style]
    width = len(marker)
    selected = text[start:end]
    if "\n" in selected or "\r" in selected:
        return None
    if start == end:
        return MarkdownEdit(start, end, marker * 2, start + width, start + width)

    if selected.startswith(marker) and selected.endswith(marker) and len(selected) > 2 * width:
        content = selected[width:-width]
        return MarkdownEdit(start, end, content, start, start + len(content))

    if (start >= width and text[start - width:start] == marker
            and text[end:end + width] == marker):
        return MarkdownEdit(start - width, end + width, selected,
                            start - width, start - width + len(selected))

    replacement = marker + selected + marker
    return MarkdownEdit(start, end, replacement, start + width, end + width)


_HEADING_PREFIX = re.compile(r"^(#{1,6})[ \t]+")


def heading_prefix_change(line: str, level: int) -> tuple[int, str]:
    """Return prefix characters to remove and replacement for H1–H3.

    Toggling the same level removes its Markdown marker; switching levels
    replaces only the marker, preserving the heading text.
    """
    if not isinstance(line, str) or "\n" in line or "\r" in line or type(level) is not int or level not in (1, 2, 3):
        raise ValueError("Heading requires one line and level 1–3")
    match = _HEADING_PREFIX.match(line)
    desired = "#" * level + " "
    if match:
        return len(match.group(0)), "" if len(match.group(1)) == level else desired
    return 0, desired
