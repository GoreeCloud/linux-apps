"""Checklist marker lookup. No side effects or file writes."""

from .markdown import FENCE, TASK


def task_marker_at_line(text: str, line_number: int):
    """Return marker column and replacement, or None."""
    if line_number < 0:
        return None
    in_fence = False
    for index, line in enumerate(text.splitlines()):
        if FENCE.match(line):
            in_fence = not in_fence
            if index == line_number:
                return None
            continue
        if index != line_number:
            continue
        if in_fence:
            return None
        match = TASK.match(line)
        if match is None:
            return None
        return match.start(1), (" " if match.group(1).lower() == "x" else "x")
    return None
