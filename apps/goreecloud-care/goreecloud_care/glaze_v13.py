"""GLAZE UI V1.3 Adaptive Resonance Development mapping for GoreeCloud Care.

GLAZE UI V1.3 is the latest Glaze UI development line, but it remains Proposed:
its Candidate is not active and downstream consumers are not yet eligible for a
production conformance grant. Care therefore treats this module as a bounded
Development consumer implementation while retaining GLAZE UI V1.2 / 1.2.0 as
the official Stable compatibility baseline.

GTK3 cannot provide compositor-authoritative backdrop sampling or the full
Living Glaze optical stack. Care maps V1.3 semantics to native Tier 1/Tier 0
surfaces: stable content planes, restrained glazed command chrome, semantic
shape roles, immediate interaction response, local-only adaptive choices, and
accessibility-first degradation. Material effects always degrade before task
correctness, readability, or input semantics.
"""
from __future__ import annotations

import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk  # noqa: E402

from .ui_contract import is_high_contrast_theme

GLAZE_UI_LABEL = "GLAZE UI V1.3 — Adaptive Resonance"
GLAZE_UI_TARGET_VERSION = "1.3.0-candidate"
GLAZE_UI_LIFECYCLE = "proposed"
GLAZE_UI_CONSUMER_ELIGIBLE = False
GLAZE_UI_SOURCE_REVISION = "dc5ee04b09bd7d2c06d6ac1456618cbd4b1f4b80"
GLAZE_UI_STABLE_BASELINE = "1.2.0"
MIN_TARGET_PX = 48

APPEARANCE_ENV = "GOREECLOUD_CARE_APPEARANCE"
EXPRESSION_ENV = "GOREECLOUD_CARE_GLAZE_EXPRESSION"
CLARITY_ENV = "GOREECLOUD_CARE_GLAZE_CLARITY"
REDUCE_TRANSPARENCY_ENV = "GOREECLOUD_CARE_REDUCE_TRANSPARENCY"
REDUCE_MOTION_ENV = "GOREECLOUD_CARE_REDUCE_MOTION"
SHOW_BORDERS_ENV = "GOREECLOUD_CARE_SHOW_BORDERS"

EXPRESSION_PROFILES = ("calm", "balanced", "expressive")
CLARITY_PROFILES = ("clear", "balanced", "dense")
LAYOUT_ENVIRONMENTS = ("compact", "medium", "expanded")

# These values are Care-local layout decisions, not raw Glaze token authority.
# GDK_DPI_SCALE-aware compact behavior remains owned by ui_contract.py.
MEDIUM_LAYOUT_WIDTH = 1040

_CSS_CLASSES = (
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
)

CSS = b"""
/* GoreeCloud Care Development mapping of Proposed GLAZE UI V1.3.
   V1.2 / 1.2.0 remains the official Stable compatibility baseline. */
window.care-shell {
  background: #eef1f5;
  color: #181a1f;
}

/* Chrome Plane: restrained neutral Glaze for command/navigation chrome only. */
window.care-shell headerbar,
window.care-shell .chrome-plane {
  background: rgba(250, 251, 252, 0.90);
  color: #181a1f;
  border-bottom: 1px solid rgba(34, 39, 48, 0.12);
}
window.care-shell headerbar button { color: inherit; }

/* Content Plane: stable reading and consequential-decision surfaces. */
window.care-shell .content-plane,
window.care-shell .surface-solid,
window.care-shell .maintenance-collection,
window.care-shell .system-panel,
window.care-shell .findings-plane {
  background: #ffffff;
  border: 1px solid rgba(34, 39, 48, 0.10);
  border-radius: 18px;
}

window.care-shell .hero-surface {
  background: rgba(255, 255, 255, 0.82);
  border: 1px solid rgba(34, 39, 48, 0.11);
  border-radius: 24px;
  padding: 18px;
}
window.care-shell .hero-mark {
  color: #2f6fed;
  font-weight: 700;
}
window.care-shell .section-title {
  font-weight: 700;
  font-size: 18px;
}
window.care-shell .eyebrow {
  color: #5c6472;
  font-weight: 700;
}
window.care-shell .muted { color: #5f6672; }
window.care-shell .warning { color: #9b6100; }
window.care-shell .metric-line { color: #4d5563; }

/* Quiet collection geometry: rows are grouped instead of cardifying each item. */
window.care-shell .maintenance-row,
window.care-shell .system-action-row {
  padding: 12px 14px;
  border-bottom: 1px solid rgba(34, 39, 48, 0.08);
}
window.care-shell .maintenance-row-last,
window.care-shell .system-action-row-last { border-bottom-width: 0; }
window.care-shell .row-title { font-weight: 700; }
window.care-shell .row-amount { color: #4d5563; font-weight: 600; }

/* Semantic status surfaces are opaque and never depend on transparency. */
window.care-shell .status-banner {
  background: #f3f7ff;
  border: 1px solid rgba(47, 111, 237, 0.34);
  border-left-width: 4px;
  border-radius: 14px;
  padding: 12px 14px;
}
window.care-shell .status-banner.status-attention {
  background: #eef8f8;
  border-color: #157b80;
}
window.care-shell .status-banner.status-success {
  background: #eef9f2;
  border-color: #2f8f5f;
}
window.care-shell .status-banner.status-error {
  background: #fff1f0;
  border-color: #bd3a32;
}
window.care-shell .status-title { color: #181a1f; font-weight: 700; }
window.care-shell .status-icon { color: #2f6fed; }
window.care-shell .status-attention .status-icon,
window.care-shell .status-attention .status-title { color: #11686c; }
window.care-shell .status-success .status-icon,
window.care-shell .status-success .status-title { color: #27784f; }
window.care-shell .status-error .status-icon,
window.care-shell .status-error .status-title { color: #a52f29; }

/* Shape roles: standard controls are rounded, capsules are opt-in. */
window.care-shell button,
window.care-shell checkbutton { min-height: 48px; }
window.care-shell button {
  border-radius: 12px;
  padding-left: 14px;
  padding-right: 14px;
}
window.care-shell button.command-capsule { border-radius: 999px; }
window.care-shell button.resonant-action {
  border-radius: 16px;
  background: #2f6fed;
  color: #ffffff;
  border-color: rgba(47, 111, 237, 0.76);
  font-weight: 700;
}
window.care-shell button.secondary-action { border-radius: 12px; }
window.care-shell button.danger-action {
  border-radius: 12px;
  color: #a52f29;
}
window.care-shell button:hover {
  box-shadow: inset 0 0 0 1px rgba(47, 111, 237, 0.18);
}
window.care-shell button.resonant-action:hover {
  box-shadow: 0 7px 18px rgba(47, 111, 237, 0.20);
}
window.care-shell button:focus,
window.care-shell checkbutton:focus,
window.care-shell label:focus {
  outline-color: #2f6fed;
  outline-style: solid;
  outline-width: 3px;
  outline-offset: 2px;
  box-shadow: 0 0 0 2px rgba(47, 111, 237, 0.26);
}

/* Expression and clarity remain separate dimensions. */
window.care-shell.expression-calm .hero-surface,
window.care-shell.expression-calm button.resonant-action:hover { box-shadow: none; }
window.care-shell.expression-balanced .hero-surface {
  box-shadow: 0 8px 24px rgba(37, 47, 65, 0.07);
}
window.care-shell.expression-expressive .hero-surface {
  box-shadow: 0 12px 30px rgba(47, 111, 237, 0.10);
  border-color: rgba(47, 111, 237, 0.18);
}
window.care-shell.clarity-clear .maintenance-row,
window.care-shell.clarity-clear .system-action-row { padding: 15px 16px; }
window.care-shell.clarity-dense .maintenance-row,
window.care-shell.clarity-dense .system-action-row { padding: 9px 12px; }

/* Dark and Deep Dark keep neutral material dominant. */
window.care-shell.care-dark {
  background: #17191c;
  color: #f7f8fa;
}
window.care-shell.care-dark headerbar,
window.care-shell.care-dark .chrome-plane {
  background: rgba(42, 45, 50, 0.92);
  color: #f7f8fa;
  border-color: rgba(255, 255, 255, 0.12);
}
window.care-shell.care-dark headerbar button {
  background: #34383f;
  background-image: none;
  color: #f7f8fa;
  border-color: rgba(255, 255, 255, 0.20);
  box-shadow: none;
}
window.care-shell.care-dark headerbar button:hover { background: #3d424a; }
window.care-shell.care-dark .content-plane,
window.care-shell.care-dark .surface-solid,
window.care-shell.care-dark .maintenance-collection,
window.care-shell.care-dark .system-panel,
window.care-shell.care-dark .findings-plane {
  background: #25282d;
  border-color: rgba(255, 255, 255, 0.11);
}
window.care-shell.care-dark .hero-surface {
  background: rgba(42, 45, 50, 0.84);
  border-color: rgba(255, 255, 255, 0.12);
}
window.care-shell.care-dark .muted,
window.care-shell.care-dark .eyebrow,
window.care-shell.care-dark .metric-line,
window.care-shell.care-dark .row-amount { color: #c8cbd2; }
window.care-shell.care-dark .warning { color: #ffd18a; }
window.care-shell.care-dark .status-title { color: #f7f8fa; }
window.care-shell.care-dark .status-banner { background: #293247; }
window.care-shell.care-dark .status-banner.status-attention { background: #203b3d; }
window.care-shell.care-dark .status-banner.status-success { background: #20382a; }
window.care-shell.care-dark .status-banner.status-error { background: #432927; }
window.care-shell.care-dark .maintenance-row,
window.care-shell.care-dark .system-action-row { border-color: rgba(255, 255, 255, 0.08); }

window.care-shell.care-deep-dark {
  background: #090a0b;
  color: #f7f8fa;
}
window.care-shell.care-deep-dark headerbar,
window.care-shell.care-deep-dark .chrome-plane {
  background: rgba(31, 33, 37, 0.94);
  color: #f7f8fa;
  border-color: rgba(255, 255, 255, 0.12);
}
window.care-shell.care-deep-dark headerbar button {
  background: #272a2f;
  background-image: none;
  color: #f7f8fa;
  border-color: rgba(255, 255, 255, 0.20);
  box-shadow: none;
}
window.care-shell.care-deep-dark headerbar button:hover { background: #30343a; }
window.care-shell.care-deep-dark .content-plane,
window.care-shell.care-deep-dark .surface-solid,
window.care-shell.care-deep-dark .maintenance-collection,
window.care-shell.care-deep-dark .system-panel,
window.care-shell.care-deep-dark .findings-plane { background: #1b1d21; }
window.care-shell.care-deep-dark .hero-surface { background: rgba(31, 33, 37, 0.86); }
window.care-shell.care-deep-dark .muted,
window.care-shell.care-deep-dark .eyebrow,
window.care-shell.care-deep-dark .metric-line,
window.care-shell.care-deep-dark .row-amount { color: #c8cbd2; }
window.care-shell.care-deep-dark .status-title { color: #f7f8fa; }
window.care-shell.care-deep-dark .status-banner { background: #252c3d; }
window.care-shell.care-deep-dark .status-banner.status-attention { background: #1d3436; }
window.care-shell.care-deep-dark .status-banner.status-success { background: #1d3226; }
window.care-shell.care-deep-dark .status-banner.status-error { background: #3b2524; }

/* Accessibility precedence: effects degrade before content or task semantics. */
window.care-shell.reduced-transparency headerbar,
window.care-shell.reduced-transparency .chrome-plane,
window.care-shell.reduced-transparency .hero-surface { background: #ffffff; }
window.care-shell.care-dark.reduced-transparency headerbar,
window.care-shell.care-dark.reduced-transparency .chrome-plane,
window.care-shell.care-dark.reduced-transparency .hero-surface { background: #2a2d32; }
window.care-shell.care-deep-dark.reduced-transparency headerbar,
window.care-shell.care-deep-dark.reduced-transparency .chrome-plane,
window.care-shell.care-deep-dark.reduced-transparency .hero-surface { background: #1f2125; }
window.care-shell.reduced-motion button:hover,
window.care-shell.reduced-motion .hero-surface { box-shadow: none; }
window.care-shell.show-borders .content-plane,
window.care-shell.show-borders .maintenance-collection,
window.care-shell.show-borders .system-panel,
window.care-shell.show-borders .findings-plane,
window.care-shell.show-borders .hero-surface { border-width: 2px; }
"""


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _choice(value: str | None, allowed: tuple[str, ...], default: str) -> str:
    normalized = (value or "").strip().lower()
    return normalized if normalized in allowed else default


def appearance_from_theme(
    theme_name: str | None,
    *,
    appearance_override: str | None = None,
    gtk_theme_override: str | None = None,
) -> str:
    override = os.environ.get(APPEARANCE_ENV) if appearance_override is None else appearance_override
    normalized_override = (override or "system").strip().lower()
    if normalized_override in {"light", "dark", "deep-dark"}:
        return normalized_override
    effective_theme = (
        os.environ.get("GTK_THEME") or theme_name or ""
        if gtk_theme_override is None
        else gtk_theme_override or theme_name or ""
    )
    normalized_theme = effective_theme.lower().replace("_", "-")
    return "dark" if "dark" in normalized_theme else "light"


def expression_profile(value: str | None = None) -> str:
    raw = os.environ.get(EXPRESSION_ENV) if value is None else value
    return _choice(raw, EXPRESSION_PROFILES, "balanced")


def clarity_profile(value: str | None = None) -> str:
    raw = os.environ.get(CLARITY_ENV) if value is None else value
    return _choice(raw, CLARITY_PROFILES, "balanced")


def reduced_transparency_requested(value: str | None = None) -> bool:
    raw = os.environ.get(REDUCE_TRANSPARENCY_ENV) if value is None else value
    return _truthy(raw)


def reduced_motion_requested(
    gtk_animations_enabled: bool | None,
    value: str | None = None,
) -> bool:
    raw = os.environ.get(REDUCE_MOTION_ENV) if value is None else value
    return _truthy(raw) or gtk_animations_enabled is False


def show_borders_requested(value: str | None = None) -> bool:
    raw = os.environ.get(SHOW_BORDERS_ENV) if value is None else value
    return _truthy(raw)


def layout_environment(effective_width: int, *, compact: bool) -> str:
    if compact:
        return "compact"
    return "medium" if effective_width < MEDIUM_LAYOUT_WIDTH else "expanded"


class GlazeV13Controller:
    """Attach the proposed V1.3 Care mapping to a single GTK3 window."""

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
        theme_name = self.settings.get_property("gtk-theme-name") if self.settings is not None else None
        high_contrast = is_high_contrast_theme(theme_name)
        self._remove_state_classes()
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
