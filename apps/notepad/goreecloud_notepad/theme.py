"""GC UI semantic Surface/Canvas design translated to native GTK CSS.

Reference: GoreeCloud/gc-ui/docs/COLOR_THEMES.md (not a stable native SDK).
"""

from gi.repository import Gdk, Gtk

STYLESHEET = """
window.notepad-window {
  background-color: #ecf0f8;
  color: #20243a;
}
window.notepad-window headerbar {
  background: #e5ebf6;
  border-bottom: 1px solid #d5dcee;
  box-shadow: none;
  min-height: 42px;
}
window.notepad-window headerbar .title {
  font-weight: 750;
  font-size: 14px;
}
window.notepad-window .header-glyph {
  border-radius: 12px;
  min-width: 32px;
  min-height: 32px;
  padding: 4px;
  margin: 3px;
}
window.notepad-window .header-glyph:hover {
  background-color: #d9def3;
}
window.notepad-window .primary-glyph {
  background-color: #e1dcff;
  color: #3c2eaa;
}
window.notepad-window notebook > header {
  background: #ecf0f8;
  padding: 3px 12px 3px 12px;
  border-bottom: 1px solid #d7deef;
}
window.notepad-window notebook > header tab {
  background: transparent;
  border: 1px solid transparent;
  border-radius: 18px;
  padding: 2px 10px;
  margin: 0 4px 0 0;
  min-width: 90px;
  min-height: 28px;
  color: #5f657b;
}
window.notepad-window notebook > header tab:hover:not(:checked) {
  background: #e5ebf6;
  color: #20243a;
}
window.notepad-window notebook > header tab:checked {
  background: #f9fafd;
  color: #20243a;
  border-color: #d7deef;
}
window.notepad-window notebook > header tab:focus-visible {
  outline: 2px solid #4132b3;
  outline-offset: -2px;
}
window.notepad-window .tab-close {
  min-width: 20px;
  min-height: 20px;
  padding: 0;
  border-radius: 999px;
}
window.notepad-window .editor-pane {
  background: #f9fafd;
}
window.notepad-window textview.notepad-editor,
window.notepad-window textview.notepad-editor text {
  background: #f9fafd;
  color: #20243a;
  caret-color: #5145d9;
}
window.notepad-window textview.notepad-editor {
  font-size: 15px;
}
window.notepad-window .notepad-footer {
  background: #e5ebf6;
  border-top: 1px solid #d7deef;
  min-height: 32px;
}
window.notepad-window .footer-label {
  color: #5f657b;
  font-size: 12px;
}
window.notepad-window .brand-dot { color: #5145d9; }
window.notepad-window.dark {
  background: #10131e;
  color: #f2f2fa;
}
window.notepad-window.dark headerbar,
window.notepad-window.dark .notepad-footer {
  background: #292f40;
  border-color: #373c50;
  color: #f2f2fa;
}
window.notepad-window.dark .footer-label { color: #b3b9cf; }
window.notepad-window.dark .brand-dot { color: #bbb2ff; }
window.notepad-window.dark .header-glyph:hover { background: #373f58; }
window.notepad-window.dark .primary-glyph { background: #403772; color: #f2f2fa; }
window.notepad-window.dark notebook > header {
  background: #10131e;
  border-color: #373c50;
}
window.notepad-window.dark notebook > header tab { color: #b3b9cf; }
window.notepad-window.dark notebook > header tab:hover:not(:checked) {
  background: #292f40;
  color: #f2f2fa;
}
window.notepad-window.dark notebook > header tab:checked {
  background: #1d2231;
  color: #f2f2fa;
  border-color: #373c50;
}
window.notepad-window.dark notebook > header tab:focus-visible {
  outline-color: #d8d2ff;
}
window.notepad-window.dark .editor-pane,
window.notepad-window.dark textview.notepad-editor,
window.notepad-window.dark textview.notepad-editor text {
  background: #1d2231;
  color: #f2f2fa;
  caret-color: #d8d2ff;
}
"""

_provider = None


def install() -> None:
    global _provider
    display = Gdk.Display.get_default()
    if display is None or _provider is not None:
        return
    _provider = Gtk.CssProvider()
    _provider.load_from_data(STYLESHEET.encode("utf-8"))
    Gtk.StyleContext.add_provider_for_display(
        display, _provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
    )
