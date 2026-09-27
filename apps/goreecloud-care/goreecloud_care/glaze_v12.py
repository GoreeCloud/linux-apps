"""GLAZE UI V1.2 native GTK3 mapping for GoreeCloud Care Development.

Care uses the V1.2 neutral-material hierarchy and accessibility degradation rules
without claiming compositor backdrop-blur authority. GTK3 therefore implements a
bounded Tier 1/Tier 0 native fallback: neutral translucent/solid application
surfaces, semantic accent/status color, 48px minimum interactive targets, no
non-essential animated optical motion, and system-authoritative HighContrast.
"""
from __future__ import annotations

import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .ui_contract import is_high_contrast_theme

GLAZE_UI_VERSION = "1.2.0"
GLAZE_UI_LABEL = "GLAZE UI V1.2"
MIN_TARGET_PX = 48
APPEARANCE_ENV = "GOREECLOUD_CARE_APPEARANCE"
REDUCE_TRANSPARENCY_ENV = "GOREECLOUD_CARE_REDUCE_TRANSPARENCY"
REDUCE_MOTION_ENV = "GOREECLOUD_CARE_REDUCE_MOTION"

_CSS_CLASSES = (
    "care-shell",
    "care-dark",
    "care-deep-dark",
    "reduced-transparency",
    "reduced-motion",
)

CSS = b"""
/* GoreeCloud Care Development mapping of current Stable GLAZE UI V1.2. */
window.care-shell {
  background: #edf0f4;
  color: #19191c;
}
headerbar {
  background: rgba(250, 250, 250, 0.88);
  color: #19191c;
  border-bottom: 1px solid rgba(45, 45, 50, 0.12);
}
headerbar button { color: inherit; }
.card {
  background: rgba(255, 255, 255, 0.72);
  border: 1px solid rgba(45, 45, 50, 0.10);
  border-radius: 20px;
  padding: 16px;
}
.status-banner {
  background: #f3f7ff;
  border: 1px solid rgba(47, 111, 237, 0.34);
  border-left-width: 4px;
  border-radius: 16px;
  padding: 12px 14px;
}
.status-banner.status-attention {
  background: #eef8f8;
  border-color: #157b80;
}
.status-banner.status-success {
  background: #eef9f2;
  border-color: #2f8f5f;
}
.status-banner.status-error {
  background: #fff1f0;
  border-color: #bd3a32;
}
.status-title { color: #19191c; font-weight: 700; }
.status-icon { color: #2f6fed; }
.status-attention .status-icon,
.status-attention .status-title { color: #11686c; }
.status-success .status-icon,
.status-success .status-title { color: #27784f; }
.status-error .status-icon,
.status-error .status-title { color: #a52f29; }
.title { font-weight: 700; font-size: 18px; }
.muted { color: #5f6671; }
.warning { color: #a66200; }
button, checkbutton { min-height: 48px; }
button {
  border-radius: 999px;
  padding-left: 14px;
  padding-right: 14px;
}
button.suggested-action {
  background: #2f6fed;
  color: #ffffff;
  border-color: rgba(47, 111, 237, 0.72);
}
/* Living Glaze is represented as an immediate bounded state change on GTK3.
   There is no cursor-following geometry, opacity drift, or non-essential motion. */
button:hover {
  box-shadow: inset 0 0 0 1px rgba(47, 111, 237, 0.18);
}
button:focus, checkbutton:focus {
  outline-color: #2f6fed;
  outline-style: solid;
  outline-width: 3px;
  outline-offset: 2px;
  box-shadow: 0 0 0 2px rgba(47, 111, 237, 0.28);
}

window.care-shell.care-dark {
  background: #18191b;
  color: #f7f7f8;
}
window.care-shell.care-dark headerbar {
  background: rgba(54, 54, 54, 0.90);
  color: #f7f7f8;
  border-color: rgba(255, 255, 255, 0.13);
}
window.care-shell.care-dark .card {
  background: rgba(41, 41, 41, 0.78);
  border-color: rgba(255, 255, 255, 0.12);
}
window.care-shell.care-dark .muted { color: #c7c9ce; }
window.care-shell.care-dark .warning { color: #ffd18a; }
window.care-shell.care-dark .status-title { color: #f7f7f8; }
window.care-shell.care-dark .status-banner { background: #293247; }
window.care-shell.care-dark .status-banner.status-attention { background: #203b3d; }
window.care-shell.care-dark .status-banner.status-success { background: #20382a; }
window.care-shell.care-dark .status-banner.status-error { background: #432927; }

window.care-shell.care-deep-dark {
  background: #090a0b;
  color: #f7f7f8;
}
window.care-shell.care-deep-dark headerbar {
  background: rgba(46, 46, 46, 0.90);
  color: #f7f7f8;
  border-color: rgba(255, 255, 255, 0.13);
}
window.care-shell.care-deep-dark .card {
  background: rgba(34, 34, 34, 0.78);
  border-color: rgba(255, 255, 255, 0.12);
}
window.care-shell.care-deep-dark .muted { color: #c7c9ce; }
window.care-shell.care-deep-dark .warning { color: #ffd18a; }
window.care-shell.care-deep-dark .status-title { color: #f7f7f8; }
window.care-shell.care-deep-dark .status-banner { background: #252c3d; }
window.care-shell.care-deep-dark .status-banner.status-attention { background: #1d3436; }
window.care-shell.care-deep-dark .status-banner.status-success { background: #1d3226; }
window.care-shell.care-deep-dark .status-banner.status-error { background: #3b2524; }

/* Reduced Transparency removes application surface sampling rather than merely
   lowering alpha. Critical semantic status surfaces are already opaque. */
window.care-shell.reduced-transparency headerbar,
window.care-shell.reduced-transparency .card { background: #ffffff; }
window.care-shell.care-dark.reduced-transparency headerbar,
window.care-shell.care-dark.reduced-transparency .card { background: #292929; }
window.care-shell.care-deep-dark.reduced-transparency headerbar,
window.care-shell.care-deep-dark.reduced-transparency .card { background: #1e1e1e; }

/* Care defines no non-essential CSS transitions or animated optical motion.
   Reduced Motion is nevertheless represented explicitly for runtime evidence. */
window.care-shell.reduced-motion button:hover { box-shadow: none; }
"""


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def appearance_from_theme(
    theme_name: str | None,
    *,
    appearance_override: str | None = None,
    gtk_theme_override: str | None = None,
) -> str:
    """Resolve Care's V1.2 appearance without overriding HighContrast authority."""
    override = (
        os.environ.get(APPEARANCE_ENV)
        if appearance_override is None
        else appearance_override
    )
    normalized_override = (override or "system").strip().lower()
    if normalized_override in {"light", "dark", "deep-dark"}:
        return normalized_override

    if gtk_theme_override is None:
        effective_theme = os.environ.get("GTK_THEME") or theme_name or ""
    else:
        effective_theme = gtk_theme_override or theme_name or ""
    normalized_theme = effective_theme.lower().replace("_", "-")
    return "dark" if "dark" in normalized_theme else "light"


def reduced_transparency_requested(value: str | None = None) -> bool:
    raw = os.environ.get(REDUCE_TRANSPARENCY_ENV) if value is None else value
    return _truthy(raw)


def reduced_motion_requested(
    gtk_animations_enabled: bool | None,
    value: str | None = None,
) -> bool:
    raw = os.environ.get(REDUCE_MOTION_ENV) if value is None else value
    if _truthy(raw):
        return True
    return gtk_animations_enabled is False


class GlazeV12Controller:
    """Attach the bounded V1.2 GTK3 material fallback to one Care window."""

    def __init__(self, window: Gtk.Window) -> None:
        self.window = window
        self.settings = Gtk.Settings.get_default()
        self.provider = Gtk.CssProvider()
        self.provider.load_from_data(CSS)
        self.provider_attached = False
        self.sync()
        if self.settings is not None:
            self.settings.connect("notify::gtk-theme-name", self._on_settings_changed)
            try:
                self.settings.connect("notify::gtk-enable-animations", self._on_settings_changed)
            except TypeError:
                pass

    def _on_settings_changed(self, *_args) -> None:
        self.sync()

    def _remove_state_classes(self) -> None:
        context = self.window.get_style_context()
        for css_class in _CSS_CLASSES:
            context.remove_class(css_class)

    def sync(self) -> None:
        screen = self.window.get_screen()
        if screen is None:
            return
        theme_name = (
            self.settings.get_property("gtk-theme-name")
            if self.settings is not None
            else None
        )
        high_contrast = is_high_contrast_theme(theme_name)
        self._remove_state_classes()

        if high_contrast:
            if self.provider_attached:
                Gtk.StyleContext.remove_provider_for_screen(screen, self.provider)
                self.provider_attached = False
            return

        if not self.provider_attached:
            Gtk.StyleContext.add_provider_for_screen(
                screen,
                self.provider,
                Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION,
            )
            self.provider_attached = True

        context = self.window.get_style_context()
        context.add_class("care-shell")
        appearance = appearance_from_theme(theme_name)
        if appearance == "dark":
            context.add_class("care-dark")
        elif appearance == "deep-dark":
            context.add_class("care-deep-dark")

        if reduced_transparency_requested():
            context.add_class("reduced-transparency")

        animations_enabled: bool | None = None
        if self.settings is not None:
            try:
                animations_enabled = bool(
                    self.settings.get_property("gtk-enable-animations")
                )
            except TypeError:
                animations_enabled = None
        if reduced_motion_requested(animations_enabled):
            context.add_class("reduced-motion")
