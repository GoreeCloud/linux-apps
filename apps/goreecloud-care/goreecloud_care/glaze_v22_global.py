"""Process-level Glaze UI 2.2 adaptation controller for GoreeCloud Care GTK3."""
from __future__ import annotations

import gi

gi.require_version("Gdk", "3.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Gdk, GLib, Gtk  # noqa: E402

from .glaze_v22 import (
    CSS,
    FORM_FACTOR_CLASSES,
    appearance_from_theme,
    clarity_profile,
    expression_profile,
    increased_contrast_requested,
    native_form_factor_for_window_width,
    reduced_effects_requested,
    reduced_motion_requested,
    reduced_transparency_requested,
    show_borders_requested,
    touch_assistance_requested,
)
from .ui_contract import is_high_contrast_theme

_PROVIDER_PRIORITY = Gtk.STYLE_PROVIDER_PRIORITY_USER - 1
_controller: "GlobalGlazeV22Controller | None" = None

_STATE_CLASSES = (
    "care-shell",
    "glaze-v22",
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
    "touch-assistance",
    "increased-contrast",
    "effects-reduced",
) + FORM_FACTOR_CLASSES[1:]


def _runtime_css(
    appearance: str,
    *,
    expression: str,
    clarity: str,
    reduced_transparency: bool,
    reduced_motion: bool,
    show_borders: bool,
    touch_assistance: bool,
    increased_contrast: bool,
    reduced_effects: bool,
) -> bytes:
    """Resolve safety-critical 2.2 state before asynchronous window binding."""
    data = CSS.replace(b"window.care-shell", b"window")
    data = data.replace(b"window.glaze-v22", b"window")
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
    if touch_assistance:
        data = data.replace(b"window.touch-assistance", b"window")
    if increased_contrast:
        data = data.replace(b"window.increased-contrast", b"window")
    if reduced_effects:
        data = data.replace(b"window.effects-reduced", b"window")
    return data


class GlobalGlazeV22Controller:
    """Synchronize 2.2 appearance, accessibility and desktop adaptation."""

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

        # Safety/accessibility state is process-resolved before the first window;
        # only allocation-derived form-factor state waits for concrete windows.
        self.sync()
        # Bind on the next GTK idle cycle rather than a fixed-delay timer. This
        # removes a startup race where a fast-created native window could render
        # process-level accessibility CSS before receiving its semantic state
        # classes (for example Touch Assistance) and window-added subscription.
        GLib.idle_add(self._attach_application)

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
        state = native_form_factor_for_window_width(int(resolved_width))
        context.add_class(f"form-factor-{state}")

    def _sync_window(self, window: Gtk.Window) -> None:
        self._clear_window_state(window)
        theme_name = self.settings.get_property("gtk-theme-name") if self.settings is not None else None
        if is_high_contrast_theme(theme_name):
            # System HighContrast owns the palette and focus presentation.
            return

        context = window.get_style_context()
        context.add_class("care-shell")
        context.add_class("glaze-v22")

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
        if touch_assistance_requested():
            context.add_class("touch-assistance")
        if increased_contrast_requested():
            context.add_class("increased-contrast")
        if reduced_effects_requested():
            context.add_class("effects-reduced")
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
                touch_assistance=touch_assistance_requested(),
                increased_contrast=increased_contrast_requested(),
                reduced_effects=reduced_effects_requested(),
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


def install_glaze_v22_global_style() -> GlobalGlazeV22Controller:
    """Install exactly one process-local Glaze UI 2.2 adoption provider."""
    global _controller
    if _controller is None:
        _controller = GlobalGlazeV22Controller()
    return _controller
