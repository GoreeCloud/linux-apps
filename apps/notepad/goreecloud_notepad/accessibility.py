"""Accessible, stable task names for native Markdown checkbox controls.

The checked state is conveyed by the CHECKBOX accessible role, not by changing
the accessible name when the user toggles a task.
"""
from __future__ import annotations

MAX_TASK_LABEL = 72


def task_accessible_name(line: int, body: str) -> str:
    """Identify the GTK source line and a concise, readable task description."""
    if line < 0:
        raise ValueError("source line must be nonnegative")
    description = " ".join(body.split())
    if not description:
        description = "Empty task"
    elif len(description) > MAX_TASK_LABEL:
        description = description[: MAX_TASK_LABEL - 1].rstrip() + "…"
    return f"Task, line {line + 1}: {description}"
