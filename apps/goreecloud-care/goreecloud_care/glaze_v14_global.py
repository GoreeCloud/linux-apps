"""Process-level GLAZE UI V1.4 Optical Intelligence controller for Care GTK3."""
from __future__ import annotations

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

from .glaze_v14 import (
    CSS,
    FORM_FACTOR_CLASSES,
    OPTICAL_CLASSES,
    appearance_from_theme,
    clarity_profile,
    expression_profile,
    increased_contrast_requested,
    native_form_factor_for_window_width,
    reduced_motion_requested,
    reduced_transparency_requested,
    show_borders_requested,
    window_optical_classes,
)
from .ui_contract import is_high_contrast_theme

_PROVIDER_PRIORITY = Gtk.STYLE_PROVIDER_PRIORITY_USER - 1
_controller: "GlobalGlazeV14Controller | None" = None

_STATE_CLASSES = (
    "care-shell",
    "glaze-v14",
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
) + FORM_FACTOR_CLASSES[1:] + OPTICAL_CLASSES


def _runtime_css(
    appearance: str,
    *,
    expression: str,
    clarity: str,
    reduced_transparency: bool,
    reduced_motion: bool,
    show_borders: bool,
) -> bytes:
    """Resolve safety-critical state before any window binding occurs."""
    data = CSS.replace(b"window.care-shell", b"window")
    data = data.replace(b"window.glaze-v14", b"window")
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


class GlobalGlazeV14Controller:
    """Synchronize current V1.4 optical/accessibility/layout state process-wide."""

    def __init__(self) -> None:
        self.settings = Gtk.Settings.get_default()
        self.screen = Gdk.Screen.get_default()
        self.provider = Gtk.CssProvider()
        self.provider_attached = False
        self._bound_windows: set[int] = set()
        self._application_handler_id: int | None = None

        if self.settings is not None:
            self.settings.connect("notify::gtk-theme-name", self._on_settings_changed)
            try:
                self.settings.connect("notify::gtk-enable-animations", self._on_settings_changed)
            except TypeError:
                pass

        self.sync()
        GLib.timeout_add(100, self._attach_application)

    def _attach_application(self) -> bool:
        app = Gtk.Application.get_default()
        if app is None:
            for window in Gtk.Window.list_toplevels():
                self._bind_window(window)
            return True
        for window in app.get_windows():
            self._bind_window(window)
        if self._application_handler_id is None:
            self._application_handler_id = app.connect("window-added", self._on_window_added)
        return False

    def _on_window_added(self, _app, window: Gtk.Window) -> None:
        self._bind_window(window)

    def _bind_window(self, window: Gtk.Window) -> None:
        identity = id(window)
        if identity in self._bound_windows:
            return
        self._bound_windows.add(identity)
        window.connect("size-allocate", self._on_size_allocate)
        self._sync_window(window)

    def _on_size_allocate(self, window: Gtk.Window, allocation) -> None:
        self._sync_form_factor(window, int(allocation.width))

    def _on_settings_changed(self, *_args) -> None:
        self.sync()

    @staticmethod
    def _clear_window_state(window: Gtk.Window) -> None:
        context = window.get_style_context()
        for css_class in _STATE_CLASSES:
            context.remove_class(css_class)

    @staticmethod
    def _sync_form_factor(window: Gtk.Window, width: int | None = None) -> None:
        context = window.get_style_context()
        for css_class in FORM_FACTOR_CLASSES[1:]:
            context.remove_class(css_class)
        resolved_width = width
        if resolved_width is None:
            resolved_width, _ = window.get_size()
        context.add_class(f"form-factor-{native_form_factor_for_window_width(int(resolved_width))}")

    def _sync_window(self, window: Gtk.Window) -> None:
        self._clear_window_state(window)
        theme_name = self.settings.get_property("gtk-theme-name") if self.settings is not None else None
        if is_high_contrast_theme(theme_name):
            # HighContrast retains system palette authority: Care's provider is
            # detached in sync(), so no product optical class may override it.
            return

        context = window.get_style_context()
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
        self._sync_form_factor(window)

    def sync(self) -> None:
        if self.screen is None:
            return
        theme_name = self.settings.get_property("gtk-theme-name") if self.settings is not None else None
        high_contrast = is_high_contrast_theme(theme_name)

        if high_contrast:
            if self.provider_attached:
                Gtk.StyleContext.remove_provider_for_screen(self.screen, self.provider)
                self.provider_attached = False
        else:
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

        for window in Gtk.Window.list_toplevels():
            self._bind_window(window)
            self._sync_window(window)


def install_glaze_v14_global_style() -> GlobalGlazeV14Controller:
    global _controller
    if _controller is None:
        _controller = GlobalGlazeV14Controller()
    return _controller
