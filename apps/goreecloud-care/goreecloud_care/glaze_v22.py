"""Glaze UI 2.2 native desktop adaptation for GoreeCloud Care.

Glaze UI 2.2.0 is the current Stable GoreeCloud design-system baseline. This
module maps the applicable 2.2 System Shell, material, accessibility, state and
native Desktop/Wide Desktop contracts onto Care's GTK3 surfaces while retaining
the previously qualified V1.4 window-adaptation behavior as regression context.

The design-system release does not certify GoreeCloud Care. Care remains a
Development / nonconformant consumer until exact-source native, rendered,
accessibility, product and external-governance acceptance are complete.
"""
from __future__ import annotations

import os

from .glaze_v14 import (
    CSS as V14_CSS,
    FORM_FACTOR_CLASSES as V14_FORM_FACTOR_CLASSES,
    appearance_from_theme,
    clarity_profile,
    expression_profile,
    layout_environment as _v14_layout_environment,
    native_form_factor_for_window_width,
    reduced_motion_requested,
    reduced_transparency_requested,
    show_borders_requested,
)

GLAZE_UI_LABEL = "GLAZE UI 2.2 — System Shell"
GLAZE_UI_TARGET_VERSION = "2.2.0"
GLAZE_UI_LIFECYCLE = "current-stable-adoption"
GLAZE_UI_ADOPTION_STATE = "development"
GLAZE_UI_CONSUMER_ELIGIBLE = False
GLAZE_UI_SOURCE_REVISION = "6731098b28dd0393faa878c70d989a221d714a20"
GLAZE_UI_RELEASE_TAG = "v2.2.0"
GLAZE_UI_APPROVED_VISUAL_SOURCE = "0411b0f6dd877aea30e2c5674e1acde0105fd97b"
GLAZE_UI_PREVIOUS_CARE_BASELINE = "1.4.0"
GLAZE_UI_UPSTREAM_ROLLBACK_BASELINE = "2.1.0"

MIN_TARGET_PX = 48
TOUCH_ASSISTANCE_TARGET_PX = 56

# Care is a native Linux desktop product. Compact/narrow are resizable-window
# adaptation states inside the Desktop contract, not claims that the app is a
# Phone, Tablet, TV, Wearable, Foldable or Spatial product.
SUPPORTED_PRODUCT_FORM_FACTORS = ("desktop", "wide-desktop")
UNSUPPORTED_PRODUCT_FORM_FACTORS = (
    "phone",
    "tablet",
    "tv",
    "foldable",
    "wearable",
    "spatial",
)

# Explicit 2.2 System Shell mapping. Existing .system-panel is an application-
# local maintenance section; it is not a Glaze System Panel authority surface.
SYSTEM_SHELL_MAPPING = {
    "workspace": "host-desktop",
    "application": "goreecloud-care-window",
    "system-overlay": "modal-confirmation-or-notice-only",
    "system-panel": "not-used-as-system-authority",
    "critical-system": "destructive-or-privileged-confirmation",
}

SYSTEM_GLAZE_BUDGET = {
    "dominant_panels_max": 1,
    "small_floating_controls_max": 3,
    "nested_backdrop_blur": False,
}

OPTIONAL_SYSTEM_SURFACES = {
    "universal_search": False,
    "control_center": False,
    "intelligence_components": False,
}

NATIVE_ACCESSIBILITY_EQUIVALENTS = {
    "forced-colors": "GTK HighContrast/system palette authority",
    "increased-contrast": "GTK HighContrast plus optional Care contrast request",
    "200-percent-text": "GTK text scaling plus reflow/scroll reachability",
    "touch-assistance": "56px Care target-floor override",
}

FORM_FACTOR_CLASSES = ("glaze-v22",) + V14_FORM_FACTOR_CLASSES[1:]


def _env_flag(name: str) -> bool:
    return os.environ.get(name, "").strip().lower() in {"1", "true", "yes", "on"}


def touch_assistance_requested() -> bool:
    return _env_flag("GOREECLOUD_CARE_TOUCH_ASSISTANCE")


def increased_contrast_requested() -> bool:
    return _env_flag("GOREECLOUD_CARE_INCREASED_CONTRAST")


def reduced_effects_requested() -> bool:
    return _env_flag("GOREECLOUD_CARE_REDUCE_EFFECTS")


def layout_environment(effective_width: int, *, compact: bool) -> str:
    """Retain Care's qualified native desktop composition transform."""
    return _v14_layout_environment(effective_width, compact=compact)


# Retain the qualified V1.4 visual/form-factor regression layer but bind it to
# the active 2.2 window class so 1.4 is no longer an active consumer identity.
_BASE_CSS = V14_CSS.replace(b"glaze-v14", b"glaze-v22")

V22_CSS = b"""
/* GoreeCloud Care native Glaze UI 2.2 mapping.
   Material principle: solid where users read or make critical decisions;
   bounded Glaze only for transient command/feedback chrome. */
window.glaze-v22 .hero-surface,
window.glaze-v22 .maintenance-collection,
window.glaze-v22 .system-panel,
window.glaze-v22 .content-plane,
window.glaze-v22 .findings-plane,
window.glaze-v22 .status-banner {
  box-shadow: none;
}

/* One bounded interactive chrome surface. Care does not create nested Glaze
   panels and does not expose Universal Search or Control Center. */
window.glaze-v22 headerbar,
window.glaze-v22 .chrome-plane {
  border-bottom-width: 1px;
  box-shadow: 0 4px 16px rgba(34, 39, 48, 0.06);
}

/* Critical/destructive and privileged actions remain certainty-first. */
window.glaze-v22 button.danger-action {
  border-width: 2px;
}
window.glaze-v22 .system-action-row button {
  min-height: 48px;
}
window.glaze-v22 .maintenance-row checkbutton {
  min-width: 48px;
  min-height: 48px;
}

/* 2.2 accessibility precedence. */
window.glaze-v22 button:focus,
window.glaze-v22 checkbutton:focus,
window.glaze-v22 label:focus {
  outline-width: 3px;
  outline-offset: 3px;
}
window.glaze-v22.touch-assistance button,
window.glaze-v22.touch-assistance checkbutton {
  min-height: 56px;
}
window.glaze-v22.touch-assistance checkbutton {
  min-width: 56px;
}
window.glaze-v22.increased-contrast .hero-surface,
window.glaze-v22.increased-contrast .maintenance-collection,
window.glaze-v22.increased-contrast .system-panel,
window.glaze-v22.increased-contrast .status-banner,
window.glaze-v22.increased-contrast button {
  border-width: 2px;
}
window.glaze-v22.increased-contrast button:focus,
window.glaze-v22.increased-contrast checkbutton:focus {
  outline-width: 4px;
}
window.glaze-v22.effects-reduced headerbar,
window.glaze-v22.effects-reduced .chrome-plane,
window.glaze-v22.reduced-transparency headerbar,
window.glaze-v22.reduced-transparency .chrome-plane,
window.glaze-v22.reduced-motion headerbar,
window.glaze-v22.reduced-motion .chrome-plane {
  box-shadow: none;
}

/* Desktop adaptation remains a semantic transform: task order and authority do
   not change at compact/narrow/desktop/wide-desktop window states. */
window.glaze-v22.form-factor-compact .hero-surface {
  padding: 14px;
}
window.glaze-v22.form-factor-wide-desktop .hero-surface {
  padding: 24px;
}
"""

CSS = _BASE_CSS + b"\n" + V22_CSS
