"""Process-level Proposed GLAZE UI V1.3 provider for GoreeCloud Care GTK3."""
from __future__ import annotations

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

from .glaze_v13 import (
    CSS,
    appearance_from_theme,
    clarity_profile,
    expression_profile,
    reduced_motion_requested,
    reduced_transparency_requested,
    show_borders_requested,
)
from .ui_contract import is_high_contrast_theme

_PROVIDER_PRIORITY = Gtk.STYLE_PROVIDER_PRIORITY_USER - 1
_controller: "GlobalGlazeV13Controller | None" = None


def _runtime_css(
    appearance: str,
    *,
    expression: str,
    clarity: str,
    reduced_transparency: bool,
    reduced_motion: bool,
    show_borders: bool,
) -> bytes:
    """Resolve the process-local V1.3 Development state without global settings."""
    data = CSS.replace(b"window.care-shell", b"window")
    if appearance == "dark":
        data = data.replace(b"window.care-dark", b"window")
    elif appearance == "deep-dark":
        data = data.replace(b"window.care-deep-dark", b"window")
    data = data.replace(f"window.expression-{expression}".encode(), b"window")
    data = data.replace(f"window.clarity-{clarity}".encode(), b"window")
    if reduced_transparency:
        data = data.replace(b"window.reduced-transparency", b"window")
    if reduced_motion:
        data = data.replace(b"window.reduced-motion", b"window")
    if show_borders:
        data = data.replace(b"window.show-borders", b"window")
    return data


class GlobalGlazeV13Controller:
    """Keep the Proposed V1.3 native mapping synchronized with GTK settings."""

    def __init__(self) -> None:
        self.settings = Gtk.Settings.get_default()
        self.screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
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

    def sync(self) -> None:
        if self.screen is None:
            return
        theme_name = self.settings.get_property("gtk-theme-name") if self.settings is not None else None
        if is_high_contrast_theme(theme_name):
            if self.provider_attached:
                Gtk.StyleContext.remove_provider_for_screen(self.screen, self.provider)
                self.provider_attached = False
            return

        animations_enabled: bool | None = None
        if self.settings is not None:
            try:
                animations_enabled = bool(self.settings.get_property("gtk-enable-animations"))
            except TypeError:
                animations_enabled = None

        runtime_css = _runtime_css(
            appearance_from_theme(theme_name),
            expression=expression_profile(),
            clarity=clarity_profile(),
            reduced_transparency=reduced_transparency_requested(),
            reduced_motion=reduced_motion_requested(animations_enabled),
            show_borders=show_borders_requested(),
        )
        self.provider.load_from_data(runtime_css)
        if not self.provider_attached:
            Gtk.StyleContext.add_provider_for_screen(
                self.screen, self.provider, _PROVIDER_PRIORITY
            )
            self.provider_attached = True


def install_glaze_v13_global_style() -> GlobalGlazeV13Controller:
    """Install exactly one process-local V1.3 Development provider."""
    global _controller
    if _controller is None:
        _controller = GlobalGlazeV13Controller()
    return _controller
