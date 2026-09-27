"""Theme-resilient keyboard-focus fallback for GoreeCloud Care."""

from __future__ import annotations

FOCUS_RESILIENCE_CSS = b"""
button:focus, checkbutton:focus {
  outline-color: @theme_fg_color;
  outline-style: solid;
  outline-width: 3px;
  outline-offset: 2px;
}
"""

_focus_provider = None


def install_focus_resilience_provider() -> bool:
    """Install a focus-only GTK provider beneath Care's normal application CSS.

    The provider intentionally sets no palette, background, border, or typography
    properties. In normal Care presentation the existing application CSS has the
    higher priority and retains the established teal focus treatment. When Care
    yields its palette to a system HighContrast theme, this lower-priority
    provider remains and draws a theme-derived focus outline so keyboard focus
    cannot become visually silent.
    """
    import gi

    gi.require_version("Gdk", "3.0")
    gi.require_version("Gtk", "3.0")
    from gi.repository import Gdk, Gtk

    screen = Gdk.Screen.get_default()
    if screen is None:
        return False

    provider = Gtk.CssProvider()
    provider.load_from_data(FOCUS_RESILIENCE_CSS)
    Gtk.StyleContext.add_provider_for_screen(
        screen,
        provider,
        Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION - 1,
    )

    global _focus_provider
    _focus_provider = provider
    return True
