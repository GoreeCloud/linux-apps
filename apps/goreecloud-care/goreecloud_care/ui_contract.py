"""Pure UI-contract helpers for GoreeCloud Care Development."""

from __future__ import annotations

import math
import os

# Normal-text compact transition. Large-text rendering uses an effective layout
# width so text scaling cannot make this breakpoint unreachable on the target GTK
# desktop while the physical window is already at its minimum usable width.
COMPACT_WIDTH = 820
MIN_WINDOW_WIDTH = 480
MIN_WINDOW_HEIGHT = 420
REGULAR_BORDER = 18
COMPACT_BORDER = 12


def _normalize_text_scale(value: object) -> float:
    try:
        scale = float(value)
    except (TypeError, ValueError):
        return 1.0
    if not math.isfinite(scale) or scale <= 0:
        return 1.0
    # A smaller font scale must not delay the normal compact transition.
    return max(1.0, scale)


def text_scale_from_environment(value: str | None = None) -> float:
    """Return the GTK text scale used by the large-text acceptance harness.

    ``GDK_DPI_SCALE`` is the GTK control used for GoreeCloud Care's 200%-text
    representative-device run. Invalid or sub-1 values fall back to the normal
    layout scale so the compact breakpoint never moves later than its baseline.
    """
    raw = os.environ.get("GDK_DPI_SCALE") if value is None else value
    return _normalize_text_scale(raw)


def effective_layout_width(width: int, text_scale: float | None = None) -> float:
    """Convert an allocated width to the width available at normal text scale."""
    scale = (
        text_scale_from_environment()
        if text_scale is None
        else _normalize_text_scale(text_scale)
    )
    return float(width) / scale


def is_compact_width(width: int, text_scale: float | None = None) -> bool:
    """Return whether Care should use its compact desktop composition."""
    return effective_layout_width(width, text_scale) < COMPACT_WIDTH


def _is_high_contrast_name(theme_name: str | None) -> bool:
    normalized = (theme_name or "").lower()
    normalized = normalized.replace("-", "").replace("_", "").replace(" ", "")
    return "highcontrast" in normalized


def is_high_contrast_theme(
    theme_name: str | None,
    gtk_theme_override: str | None = None,
) -> bool:
    """Return whether GTK HighContrast is active or explicitly requested.

    ``Gtk.Settings:gtk-theme-name`` does not necessarily reflect a process-local
    ``GTK_THEME`` override. GoreeCloud Care's representative-device accessibility
    harness intentionally launches isolated HighContrast processes using that
    override, so both sources are part of the effective theme contract.
    """
    if _is_high_contrast_name(theme_name):
        return True
    override = (
        os.environ.get("GTK_THEME")
        if gtk_theme_override is None
        else gtk_theme_override
    )
    return _is_high_contrast_name(override)
