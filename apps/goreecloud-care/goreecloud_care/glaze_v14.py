"""GLAZE UI V1.4 form-factor adaptation for GoreeCloud Care.

Glaze UI 1.4.0 is a historical Stable design-system release that extends the
1.3 expressive/material foundation with first-class form-factor semantics.
Downstream applications are not certified merely because the design-system
release is Stable, so this module deliberately describes Care as an adoption
candidate until application-specific validation is accepted.

Care is a GTK3 desktop application. It therefore maps the V1.4 Desktop and Wide
Desktop contracts to native GTK surfaces while keeping compact/narrow window
behavior task-complete. Unsupported optical effects degrade before content,
focus, readability, or maintenance correctness.
"""
from __future__ import annotations

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .glaze_v13 import (
    CSS as V13_CSS,
    appearance_from_theme,
    clarity_profile,
    expression_profile,
    reduced_motion_requested,
    reduced_transparency_requested,
    show_borders_requested,
)
from .ui_contract import effective_layout_width, is_compact_width, is_high_contrast_theme

GLAZE_UI_LABEL = "GLAZE UI V1.4 — Form-Factor Evolution"
GLAZE_UI_TARGET_VERSION = "1.4.0"
GLAZE_UI_LIFECYCLE = "historical-stable-adoption"
GLAZE_UI_ADOPTION_STATE = "development"
GLAZE_UI_CONSUMER_ELIGIBLE = False
# Canonical Stable promotion commit recorded by the Glaze UI 1.4.0 changelog.
GLAZE_UI_SOURCE_REVISION = "01c86323f8b747373d308026adc8b0881855cdc5"
GLAZE_UI_PREVIOUS_BASELINE = "1.3.0"
MIN_TARGET_PX = 48

FORM_FACTOR_COMPACT_MAX = 759
FORM_FACTOR_NARROW_DESKTOP_MAX = 1023
FORM_FACTOR_DESKTOP_MAX = 1199
FORM_FACTOR_CLASSES = (
    "glaze-v14",
    "form-factor-compact",
    "form-factor-narrow-desktop",
    "form-factor-desktop",
    "form-factor-wide-desktop",
)


def form_factor_environment(effective_width: int, *, compact: bool = False) -> str:
    """Resolve Care's V1.4 native composition state from effective width.

    Width is only a native window-composition input here; it does not relabel a
    desktop Care process as a Mobile, Tablet, or TV product. The V1.4 platform
    contract remains Desktop/Wide Desktop for this application.
    """
    width = max(0, int(effective_width))
    if compact or width <= FORM_FACTOR_COMPACT_MAX:
        return "compact"
    if width <= FORM_FACTOR_NARROW_DESKTOP_MAX:
        return "narrow-desktop"
    if width <= FORM_FACTOR_DESKTOP_MAX:
        return "desktop"
    return "wide-desktop"


def native_form_factor_for_window_width(raw_width: int) -> str:
    """Resolve a GTK allocation through Care's DPI-aware width contract."""
    width = max(0, int(raw_width))
    return form_factor_environment(
        int(effective_layout_width(width)),
        compact=is_compact_width(width),
    )


def layout_environment(effective_width: int, *, compact: bool) -> str:
    """Compatibility layout result for existing Care composition code."""
    state = form_factor_environment(effective_width, compact=compact)
    if state == "compact":
        return "compact"
    if state == "narrow-desktop":
        return "medium"
    return "expanded"


V14_CSS = b"""
/* GoreeCloud Care native adaptation of Glaze UI V1.4.
   Functional glass is restricted to command chrome. Stable reading and
   consequential-action surfaces remain opaque or near-opaque. */
window.glaze-v14 headerbar,
window.glaze-v14 .chrome-plane {
  border-bottom-width: 1px;
  box-shadow: 0 5px 20px rgba(34, 39, 48, 0.06);
}

window.glaze-v14 .hero-surface {
  border-radius: 26px;
  padding: 20px;
}
window.glaze-v14 .maintenance-collection,
window.glaze-v14 .system-panel,
window.glaze-v14 .content-plane,
window.glaze-v14 .findings-plane {
  border-radius: 20px;
}
window.glaze-v14 .status-banner {
  border-radius: 16px;
}
window.glaze-v14 button {
  border-radius: 14px;
}
window.glaze-v14 button.command-capsule {
  border-radius: 999px;
}
window.glaze-v14 button.resonant-action {
  border-radius: 18px;
}

/* V1.4 compact/native-window adaptation. Task order is unchanged. */
window.glaze-v14.form-factor-compact .hero-surface {
  border-radius: 18px;
  padding: 14px;
  box-shadow: none;
}
window.glaze-v14.form-factor-compact .maintenance-collection,
window.glaze-v14.form-factor-compact .system-panel,
window.glaze-v14.form-factor-compact .content-plane,
window.glaze-v14.form-factor-compact .findings-plane {
  border-radius: 16px;
}
window.glaze-v14.form-factor-compact .section-title {
  font-size: 17px;
}

/* Narrow desktop preserves one reading column before multi-pane composition. */
window.glaze-v14.form-factor-narrow-desktop .hero-surface {
  padding: 17px;
}

/* Desktop is the canonical Care composition. */
window.glaze-v14.form-factor-desktop .hero-surface {
  padding: 20px;
}
window.glaze-v14.form-factor-desktop .maintenance-row,
window.glaze-v14.form-factor-desktop .system-action-row {
  padding-top: 13px;
  padding-bottom: 13px;
}

/* Wide Desktop increases breathing room, never target density or text scale
   merely to fill pixels. */
window.glaze-v14.form-factor-wide-desktop .hero-surface {
  padding: 24px;
  box-shadow: 0 14px 34px rgba(37, 47, 65, 0.08);
}
window.glaze-v14.form-factor-wide-desktop .section-title {
  font-size: 19px;
}
window.glaze-v14.form-factor-wide-desktop .maintenance-row,
window.glaze-v14.form-factor-wide-desktop .system-action-row {
  padding-top: 15px;
  padding-bottom: 15px;
}

/* Input semantics remain visible independently of material effects. */
window.glaze-v14 button:focus,
window.glaze-v14 checkbutton:focus,
window.glaze-v14 label:focus {
  outline-width: 3px;
  outline-offset: 3px;
}

/* Accessibility precedence: remove embellishment before hierarchy or focus. */
window.glaze-v14.reduced-transparency headerbar,
window.glaze-v14.reduced-transparency .chrome-plane,
window.glaze-v14.reduced-transparency .hero-surface {
  box-shadow: none;
}
window.glaze-v14.reduced-motion headerbar,
window.glaze-v14.reduced-motion .chrome-plane,
window.glaze-v14.reduced-motion .hero-surface,
window.glaze-v14.reduced-motion button:hover {
  box-shadow: none;
}
window.glaze-v14.show-borders .hero-surface,
window.glaze-v14.show-borders .maintenance-collection,
window.glaze-v14.show-borders .system-panel,
window.glaze-v14.show-borders .content-plane,
window.glaze-v14.show-borders .findings-plane {
  border-width: 2px;
}
"""

# V1.4 intentionally inherits the accepted expressive/material semantics of the
# V1.3 mapping and adds form-factor composition on top.
CSS = V13_CSS + b"\n" + V14_CSS


class GlazeV14Controller:
    """Attach the V1.4 Care adaptation and form-factor state to one GTK3 window."""

    def __init__(self, window: Gtk.Window) -> None:
        self.window = window
        self.settings = Gtk.Settings.get_default()
        self.provider = Gtk.CssProvider()
        self.provider.load_from_data(CSS)
        self.provider_attached = False
        self.window.connect("size-allocate", self._on_size_allocate)
        self.sync()

        if self.settings is not None:
            self.settings.connect("notify::gtk-theme-name", self._on_settings_changed)
            try:
                self.settings.connect("notify::gtk-enable-animations", self._on_settings_changed)
            except TypeError:
                pass

    def _on_settings_changed(self, *_args) -> None:
        self.sync()

    def _on_size_allocate(self, _widget, allocation) -> None:
        self._sync_form_factor(int(allocation.width))

    def _clear_classes(self) -> None:
        context = self.window.get_style_context()
        for css_class in FORM_FACTOR_CLASSES:
            context.remove_class(css_class)
        for css_class in (
            "care-shell",
            "care-dark",
            "care-deep-dark",
            "expression-calm",
            "expression-balanced",
            "expression-expressive",
            "clarity-clear",
            "clarity-balanced",
            "clarity-dense",
            "reduced-transparency",
            "reduced-motion",
            "show-borders",
        ):
            context.remove_class(css_class)

    def _sync_form_factor(self, width: int | None = None) -> None:
        context = self.window.get_style_context()
        for css_class in FORM_FACTOR_CLASSES[1:]:
            context.remove_class(css_class)
        resolved_width = width
        if resolved_width is None:
            resolved_width, _ = self.window.get_size()
        context.add_class(
            f"form-factor-{native_form_factor_for_window_width(int(resolved_width))}"
        )

    def sync(self) -> None:
        screen = self.window.get_screen()
        if screen is None:
            return
        theme_name = self.settings.get_property("gtk-theme-name") if self.settings is not None else None
        high_contrast = is_high_contrast_theme(theme_name)
        self._clear_classes()
        if high_contrast:
            if self.provider_attached:
                Gtk.StyleContext.remove_provider_for_screen(screen, self.provider)
                self.provider_attached = False
            return

        if not self.provider_attached:
            Gtk.StyleContext.add_provider_for_screen(
                screen, self.provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            self.provider_attached = True

        context = self.window.get_style_context()
        context.add_class("care-shell")
        context.add_class("glaze-v14")
        appearance = appearance_from_theme(theme_name)
        if appearance == "dark":
            context.add_class("care-dark")
        elif appearance == "deep-dark":
            context.add_class("care-deep-dark")
        context.add_class(f"expression-{expression_profile()}")
        context.add_class(f"clarity-{clarity_profile()}")
        if reduced_transparency_requested():
            context.add_class("reduced-transparency")
        animations_enabled: bool | None = None
        if self.settings is not None:
            try:
                animations_enabled = bool(self.settings.get_property("gtk-enable-animations"))
            except TypeError:
                animations_enabled = None
        if reduced_motion_requested(animations_enabled):
            context.add_class("reduced-motion")
        if show_borders_requested():
            context.add_class("show-borders")
        self._sync_form_factor()
