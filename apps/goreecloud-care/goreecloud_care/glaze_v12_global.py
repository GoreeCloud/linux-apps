"""Process-level GLAZE UI V1.2 provider for GoreeCloud Care GTK3 windows."""
from __future__ import annotations

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from .glaze_v12 import (
    CSS,
    appearance_from_theme,
    reduced_motion_requested,
    reduced_transparency_requested,
)
from .ui_contract import is_high_contrast_theme

_PROVIDER_PRIORITY = Gtk.STYLE_PROVIDER_PRIORITY_USER - 1
_controller: "GlobalGlazeV12Controller | None" = None


def _runtime_css(
    appearance: str,
    *,
    reduced_transparency: bool,
    reduced_motion: bool,
) -> bytes:
    """Make the process-local Care selectors active for the resolved state.

    The canonical source keeps explicit state classes so the contract is readable
    and testable. Care is a single-product process, so this installed provider may
    safely promote the resolved state selectors to generic window selectors rather
    than requiring every current GTK3 window class to duplicate appearance logic.
    """
    data = CSS.replace(b"window.care-shell", b"window")
    if appearance == "dark":
        data = data.replace(b"window.care-dark", b"window")
    elif appearance == "deep-dark":
        data = data.replace(b"window.care-deep-dark", b"window")
    if reduced_transparency:
        data = data.replace(b"window.reduced-transparency", b"window")
    if reduced_motion:
        data = data.replace(b"window.reduced-motion", b"window")
    return data


class GlobalGlazeV12Controller:
    """Keep the V1.2 native fallback synchronized with effective GTK settings."""

    def __init__(self) -> None:
        self.settings = Gtk.Settings.get_default()
        self.screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
        self.provider_attached = False
        self.sync()
        if self.settings is not None:
            self.settings.connect("notify::gtk-theme-name", self._on_settings_changed)
            try:
                self.settings.connect(
                    "notify::gtk-enable-animations", self._on_settings_changed
                )
            except TypeError:
                pass

    def _on_settings_changed(self, *_args) -> None:
        self.sync()

    def sync(self) -> None:
        if self.screen is None:
            return
        theme_name = (
            self.settings.get_property("gtk-theme-name")
            if self.settings is not None
            else None
        )
        if is_high_contrast_theme(theme_name):
            if self.provider_attached:
                Gtk.StyleContext.remove_provider_for_screen(
                    self.screen, self.provider
                )
                self.provider_attached = False
            return

        animations_enabled: bool | None = None
        if self.settings is not None:
            try:
                animations_enabled = bool(
                    self.settings.get_property("gtk-enable-animations")
                )
            except TypeError:
                animations_enabled = None

        runtime_css = _runtime_css(
            appearance_from_theme(theme_name),
            reduced_transparency=reduced_transparency_requested(),
            reduced_motion=reduced_motion_requested(animations_enabled),
        )
        self.provider.load_from_data(runtime_css)
        if not self.provider_attached:
            Gtk.StyleContext.add_provider_for_screen(
                self.screen,
                self.provider,
                _PROVIDER_PRIORITY,
            )
            self.provider_attached = True


def install_glaze_v12_global_style() -> GlobalGlazeV12Controller:
    """Install exactly one process-local V1.2 provider and retain its lifetime."""
    global _controller
    if _controller is None:
        _controller = GlobalGlazeV12Controller()
    return _controller
