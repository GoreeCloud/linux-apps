"""GLAZE UI V1.4.1 Optical Intelligence adaptation for GoreeCloud Care.

The current Glaze UI authority defines 1.4.1 as Official Stable in the V1.4
Optical Intelligence family. Care maps that contract to GTK3 conservatively:
optical adaptation is local and deterministic, accessibility always outranks
decoration, adapter faults fail safe, and unsupported compositor effects
degrade before content, focus, or maintenance correctness.

Care's compact/narrow/desktop/wide window states remain application-owned GTK
layout behavior. They are useful responsive behavior, but they are not treated
as the definition of the V1.4 design-system release.
"""
from __future__ import annotations

import os

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
from .glaze_v14_optical import care_default_optical_state, optical_css_classes
from .ui_contract import effective_layout_width, is_compact_width, is_high_contrast_theme

GLAZE_UI_LABEL = "GLAZE UI V1.4 — Optical Intelligence"
GLAZE_UI_TARGET_VERSION = "1.4.1"
GLAZE_UI_LIFECYCLE = "official-stable-adoption"
GLAZE_UI_ADOPTION_STATE = "development"
GLAZE_UI_CONSUMER_ELIGIBLE = False
GLAZE_UI_SOURCE_REVISION = "4fab9da0fad2e5c974e0e66ec88632c61745751c"
GLAZE_UI_SOURCE_QUALIFICATION_ANCHOR = "66478aed461b83c49b2ed027c3e4afc26520e98c"
# Historical V1.4.0 integration anchor retained for audit/reference compatibility.
GLAZE_UI_SOURCE_INTEGRATION_ANCHOR = "a20374734dae6a119b28448f5e6b3232253b6da7"
GLAZE_UI_PREVIOUS_BASELINE = "1.4.0"
MIN_TARGET_PX = 48

INCREASED_CONTRAST_ENV = "GOREECLOUD_CARE_INCREASED_CONTRAST"

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
OPTICAL_CLASSES = (
    "optical-adaptive-optical",
    "optical-solid-accessible",
    "optical-frost-soft",
    "optical-frost-balanced",
    "optical-frost-strong",
    "optical-semantic-protected",
    "optical-depth-base",
    "optical-depth-raised",
    "optical-depth-overlay",
    "optical-depth-modal",
    "optical-no-decorative-tint",
)


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def increased_contrast_requested(value: str | None = None) -> bool:
    """Return Care's explicit Increased Contrast preference when provided."""
    raw = os.environ.get(INCREASED_CONTRAST_ENV) if value is None else value
    return _truthy(raw)


def form_factor_environment(effective_width: int, *, compact: bool = False) -> str:
    """Resolve Care-owned native desktop composition from effective width."""
    width = max(0, int(effective_width))
    if compact or width <= FORM_FACTOR_COMPACT_MAX:
        return "compact"
    if width <= FORM_FACTOR_NARROW_DESKTOP_MAX:
        return "narrow-desktop"
    if width <= FORM_FACTOR_DESKTOP_MAX:
        return "desktop"
    return "wide-desktop"


def native_form_factor_for_window_width(raw_width: int) -> str:
    width = max(0, int(raw_width))
    return form_factor_environment(
        int(effective_layout_width(width)), compact=is_compact_width(width)
    )


def layout_environment(effective_width: int, *, compact: bool) -> str:
    state = form_factor_environment(effective_width, compact=compact)
    if state == "compact":
        return "compact"
    if state == "narrow-desktop":
        return "medium"
    return "expanded"


def window_optical_classes(
    appearance: str,
    *,
    reduced_transparency: bool,
    reduced_motion: bool,
    increased_contrast: bool,
    forced_colors: bool = False,
) -> tuple[str, ...]:
    state = care_default_optical_state(
        appearance=appearance,
        reduced_transparency=reduced_transparency,
        reduced_motion=reduced_motion,
        increased_contrast=increased_contrast,
        forced_colors=forced_colors,
        depth="base",
        semantic_importance=0.80,
    )
    return optical_css_classes(state)


V14_CSS = b"""
/* Care maps V1.4.1 Optical Intelligence into bounded GTK3 native treatment.
   GTK3 does not claim compositor-authoritative backdrop sampling or blur. */
window.glaze-v14.optical-adaptive-optical headerbar,
window.glaze-v14.optical-adaptive-optical .chrome-plane {
  border-bottom-width: 1px;
  box-shadow: 0 5px 20px rgba(34, 39, 48, 0.06);
}
window.glaze-v14.optical-frost-soft headerbar,
window.glaze-v14.optical-frost-soft .chrome-plane { box-shadow: 0 3px 12px rgba(34, 39, 48, 0.04); }
window.glaze-v14.optical-frost-balanced headerbar,
window.glaze-v14.optical-frost-balanced .chrome-plane { box-shadow: 0 5px 20px rgba(34, 39, 48, 0.06); }
window.glaze-v14.optical-frost-strong headerbar,
window.glaze-v14.optical-frost-strong .chrome-plane { box-shadow: 0 7px 24px rgba(34, 39, 48, 0.08); }
window.glaze-v14.optical-semantic-protected .content-plane,
window.glaze-v14.optical-semantic-protected .maintenance-collection,
window.glaze-v14.optical-semantic-protected .system-panel,
window.glaze-v14.optical-semantic-protected .findings-plane,
window.glaze-v14.optical-semantic-protected .status-banner { box-shadow: none; }
window.glaze-v14.optical-solid-accessible headerbar,
window.glaze-v14.optical-solid-accessible .chrome-plane,
window.glaze-v14.optical-solid-accessible .hero-surface,
window.glaze-v14.optical-no-decorative-tint .hero-surface { box-shadow: none; }

/* Care-owned responsive desktop composition remains separate from Glaze identity. */
window.glaze-v14 .hero-surface { border-radius: 26px; padding: 20px; }
window.glaze-v14 .maintenance-collection,
window.glaze-v14 .system-panel,
window.glaze-v14 .content-plane,
window.glaze-v14 .findings-plane { border-radius: 20px; }
window.glaze-v14 .status-banner { border-radius: 16px; }
window.glaze-v14 button { border-radius: 14px; }
window.glaze-v14 button.command-capsule { border-radius: 999px; }
window.glaze-v14 button.resonant-action { border-radius: 18px; }
window.glaze-v14.form-factor-compact .hero-surface {
  border-radius: 18px; padding: 14px; box-shadow: none;
}
window.glaze-v14.form-factor-compact .maintenance-collection,
window.glaze-v14.form-factor-compact .system-panel,
window.glaze-v14.form-factor-compact .content-plane,
window.glaze-v14.form-factor-compact .findings-plane { border-radius: 16px; }
window.glaze-v14.form-factor-compact .section-title { font-size: 17px; }
window.glaze-v14.form-factor-narrow-desktop .hero-surface { padding: 17px; }
window.glaze-v14.form-factor-desktop .hero-surface { padding: 20px; }
window.glaze-v14.form-factor-desktop .maintenance-row,
window.glaze-v14.form-factor-desktop .system-action-row { padding-top: 13px; padding-bottom: 13px; }
window.glaze-v14.form-factor-wide-desktop .hero-surface {
  padding: 24px; box-shadow: 0 14px 34px rgba(37, 47, 65, 0.08);
}
window.glaze-v14.form-factor-wide-desktop .section-title { font-size: 19px; }
window.glaze-v14.form-factor-wide-desktop .maintenance-row,
window.glaze-v14.form-factor-wide-desktop .system-action-row { padding-top: 15px; padding-bottom: 15px; }
window.glaze-v14 button:focus,
window.glaze-v14 checkbutton:focus,
window.glaze-v14 label:focus { outline-width: 3px; outline-offset: 3px; }
window.glaze-v14.reduced-transparency headerbar,
window.glaze-v14.reduced-transparency .chrome-plane,
window.glaze-v14.reduced-transparency .hero-surface,
window.glaze-v14.reduced-motion headerbar,
window.glaze-v14.reduced-motion .chrome-plane,
window.glaze-v14.reduced-motion .hero-surface,
window.glaze-v14.reduced-motion button:hover { box-shadow: none; }
window.glaze-v14.show-borders .hero-surface,
window.glaze-v14.show-borders .maintenance-collection,
window.glaze-v14.show-borders .system-panel,
window.glaze-v14.show-borders .content-plane,
window.glaze-v14.show-borders .findings-plane { border-width: 2px; }
"""

CSS = V13_CSS + b"\n" + V14_CSS


class GlazeV14Controller:
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
        for css_class in FORM_FACTOR_CLASSES + OPTICAL_CLASSES + (
            "care-shell", "care-dark", "care-deep-dark",
            "expression-calm", "expression-balanced", "expression-expressive",
            "clarity-clear", "clarity-balanced", "clarity-dense",
            "reduced-transparency", "reduced-motion", "show-borders",
        ):
            context.remove_class(css_class)

    def _sync_form_factor(self, width: int | None = None) -> None:
        context = self.window.get_style_context()
        for css_class in FORM_FACTOR_CLASSES[1:]:
            context.remove_class(css_class)
        resolved_width = width
        if resolved_width is None:
            resolved_width, _ = self.window.get_size()
        context.add_class(f"form-factor-{native_form_factor_for_window_width(int(resolved_width))}")

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
        reduced_transparency = reduced_transparency_requested()
        if reduced_transparency:
            context.add_class("reduced-transparency")
        animations_enabled: bool | None = None
        if self.settings is not None:
            try:
                animations_enabled = bool(self.settings.get_property("gtk-enable-animations"))
            except TypeError:
                animations_enabled = None
        reduced_motion = reduced_motion_requested(animations_enabled)
        if reduced_motion:
            context.add_class("reduced-motion")
        if show_borders_requested():
            context.add_class("show-borders")
        for css_class in window_optical_classes(
            appearance,
            reduced_transparency=reduced_transparency,
            reduced_motion=reduced_motion,
            increased_contrast=increased_contrast_requested(),
        ):
            context.add_class(css_class)
        self._sync_form_factor()
