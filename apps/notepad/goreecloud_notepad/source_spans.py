"""Source-preserving Markdown styling spans for an editable GTK TextBuffer.

Only returns character offsets and tag names. Neither the parser nor its
consumer changes source text, filesystem contents, or undo history.
"""
from __future__ import annotations

from dataclasses import dataclass

from .markdown import FENCE, HEADING, INLINE, BULLET, ORDERED, QUOTE, TASK


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    style: str


MAX_STYLED_CHARS = 100_000
MAX_STYLED_SPANS = 2_500


def source_spans(text: str) -> list[Span]:
    """Recognize a deliberately limited Markdown subset, without HTML parsing.

    All offsets are Unicode character positions. Long documents are left plain
    rather than rescanned on each keystroke.
    """
    if len(text) > MAX_STYLED_CHARS:
        return []
    spans: list[Span] = []
    offset = 0
    in_fence = False

    def add(start: int, end: int, kind: str):
        if end > start:
            spans.append(Span(offset + start, offset + end, kind))

    for segment in text.splitlines(keepends=True):
        raw = segment.rstrip("\r\n")
        if FENCE.match(raw):
            add(0, len(raw), "marker")
            in_fence = not in_fence
        elif in_fence:
            add(0, len(raw), "code")
        elif raw:
            heading = HEADING.match(raw)
            task = TASK.match(raw)
            bullet = BULLET.match(raw)
            ordered = ORDERED.match(raw)
            quote = QUOTE.match(raw)

            if heading:
                add(heading.start(2), heading.end(2),
                    "h" + str(len(heading.group(1))))
                add(heading.start(1), heading.end(1), "marker")
            elif task:
                add(task.start(1) - 1, task.end(1) + 1, "task")
                add(task.start(), task.start(1) - 1, "marker")
            elif bullet:
                add(bullet.start(), bullet.start(1), "list")
            elif ordered:
                add(ordered.start(), ordered.start(2), "list")
            elif quote:
                add(quote.start(), quote.start(1), "quote")

            for match in INLINE.finditer(raw):
                for style, group in (
                    ("bold", 2), ("bold", 3), ("strike", 4),
                    ("code", 5), ("italic", 6), ("italic", 7), ("link", 8),
                ):
                    if match.group(group) is not None:
                        add(match.start(group), match.end(group), style)
                        add(match.start(), match.start(group), "marker")
                        add(match.end(group), match.end(), "marker")
                        break
        if len(spans) > MAX_STYLED_SPANS:
            return []  # Keep markup-heavy notes responsive and consistently plain.
        offset += len(segment)
    return spans
