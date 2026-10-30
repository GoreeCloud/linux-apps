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
  background: #edf2f9;
  border-bottom: 0;
  box-shadow: none;
  min-height: 54px;
  padding: 0 15px;
}
window.notepad-window .brand-identity {
  font-size: 16px;
  font-weight: 700;
  color: #18263c;
}
window.notepad-window .brand-identity image { color: #2169d5; }
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
  background: #dceaff;
  color: #183c7d;
  border-color: #c7dbfa;
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
window.notepad-window .paper-pane { border: 1px solid #d8e0eb; border-radius: 18px; background: #ffffff; }
window.notepad-window .editor-pane {
  background: #ffffff;
  border-radius: 17px;
}
window.notepad-window textview.notepad-editor,
window.notepad-window textview.notepad-editor text {
  background: #ffffff;
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

/* GoreeCloud Notepad native desktop shell; GC UI semantic surfaces. */
window.notepad-window headerbar {
  background: #edf2f9;
  padding: 0 15px;
}
window.notepad-window .header-glyph {
  color: #273a55;
  min-width: 34px;
  min-height: 34px;
  border-radius: 12px;
}
window.notepad-window notebook > header {
  background: #edf2f9;
  padding: 5px 16px 0 16px;
  border-bottom: 0;
}
window.notepad-window notebook > header tab {
  background: #f3f6fb;
  border: 1px solid #d9e1ee;
  border-radius: 18px 18px 0 0;
  min-width: 188px;
  min-height: 28px;
  padding: 5px 11px;
  margin: 0 4px 0 0;
  color: #30435e;
}
window.notepad-window notebook > header tab:checked {
  background: #dceaff;
  border-color: #c7dafa;
  color: #153e83;
}
window.notepad-window notebook > header tab:hover:not(:checked) {
  background: #e8eef8;
  color: #20243a;
}
window.notepad-window .tab-add {
  background: #e5ecf7;
  border: 1px solid #dae3ee;
  border-radius: 999px;
  margin: 4px 8px 4px 7px;
  min-width: 30px;
  min-height: 30px;
}
window.notepad-window .paper-pane {
  background: #ffffff;
  border: 1px solid #d9e1ed;
  border-radius: 18px;
  box-shadow: 0 3px 14px rgba(37, 53, 81, 0.10);
}
window.notepad-window .editor-pane {
  background: #ffffff;
  border-radius: 17px;
}
window.notepad-window textview.notepad-editor,
window.notepad-window textview.notepad-editor text {
  background: #ffffff;
  color: #20243a;
}
window.notepad-window .notepad-footer {
  background: #edf2f9;
  border-top: 0;
  min-height: 34px;
}
window.notepad-window .notepad-footer separator {
  background: #c8d4e5;
  margin: 5px 8px;
}
window.notepad-window.dark headerbar,
window.notepad-window.dark notebook > header,
window.notepad-window.dark .notepad-footer {
  background: #202a3a;
  border-color: #414b5f;
}
window.notepad-window.dark .brand-identity {
  color: #f2f2fa;
}
window.notepad-window.dark .brand-identity image {
  color: #9bbaff;
}
window.notepad-window.dark .header-glyph {
  color: #e5eafa;
}
window.notepad-window.dark notebook > header tab {
  background: #273247;
  border-color: #3b4962;
  color: #c9d3e5;
}
window.notepad-window.dark notebook > header tab:checked {
  background: #334c79;
  border-color: #5475b0;
  color: #f4f7ff;
}
window.notepad-window.dark notebook > header tab:hover:not(:checked) {
  background: #38465e;
  color: #ffffff;
}
window.notepad-window.dark .tab-add {
  background: #344259;
  border-color: #485876;
  color: #f0f4ff;
}
window.notepad-window.dark .paper-pane {
  background: #1d2636;
  border-color: #3e4d66;
  box-shadow: 0 3px 14px rgba(0, 0, 0, 0.22);
}
window.notepad-window.dark .editor-pane,
window.notepad-window.dark textview.notepad-editor,
window.notepad-window.dark textview.notepad-editor text {
  background: #1d2636;
  color: #f2f2fa;
}
window.notepad-window.dark .notepad-footer separator {
  background: #526075;
}

"""

STYLESHEET += """
/* Compact, native document search. */
window.notepad-window .notepad-findbar {
  background: #edf2f9;
  color: #283b56;
  border-radius: 12px;
  padding: 5px 8px;
}
window.notepad-window .notepad-findbar entry {
  background: #ffffff;
  color: #20243a;
  border-radius: 11px;
  min-height: 34px;
  border: 1px solid #cbd9ec;
}
window.notepad-window .find-glyph {
  border-radius: 10px;
  min-height: 30px;
  min-width: 30px;
  padding: 3px;
}
window.notepad-window .find-glyph:hover {
  background: #dceaff;
}
window.notepad-window.dark .notepad-findbar {
  background: #202a3a;
  color: #edf2fa;
}
window.notepad-window.dark .notepad-findbar entry {
  background: #1d2636;
  color: #f2f2fa;
  border-color: #53627e;
}
window.notepad-window.dark .find-glyph:hover {
  background: #334c79;
}
"""

STYLESHEET += """
/* Read-only native Markdown preview shares the editor paper surface. */
window.notepad-window textview.notepad-preview,
window.notepad-window textview.notepad-preview text {
  background: #ffffff;
  color: #20243a;
  font-size: 15px;
}
window.notepad-window.dark textview.notepad-preview,
window.notepad-window.dark textview.notepad-preview text {
  background: #1d2636;
  color: #f2f2fa;
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

STYLESHEET += """
/* The last document carries the New Tab button as a peer of its pill.
   Keep GTK Notebook's supported scrolling/reordering and focus behavior. */
window.notepad-window notebook > header tab {
  background: transparent;
  border: none;
  border-radius: 0;
  min-width: 0;
  padding: 0;
  margin: 0 3px 0 0;
}
window.notepad-window notebook > header tab:hover:not(:checked) {
  background: transparent;
}
window.notepad-window notebook > header tab .document-tab {
  background: #f3f6fb;
  border: 1px solid #d9e1ee;
  border-radius: 18px 18px 0 0;
  min-width: 188px;
  min-height: 28px;
  padding: 5px 11px;
  color: #30435e;
}
window.notepad-window notebook > header tab:checked .document-tab {
  background: #dceaff;
  border-color: #c7dafa;
  color: #153e83;
}
window.notepad-window notebook > header tab:hover:not(:checked) .document-tab {
  background: #e8eef8;
  color: #20243a;
}
window.notepad-window notebook > header tab .tab-add {
  border-radius: 999px;
  min-width: 30px;
  min-height: 30px;
  padding: 2px;
  margin: 3px 1px 3px 4px;
}
window.notepad-window.dark notebook > header tab {
  background: transparent;
  border: none;
}
window.notepad-window.dark notebook > header tab .document-tab {
  background: #273247;
  color: #c9d3e5;
  border-color: #3b4962;
}
window.notepad-window.dark notebook > header tab:checked .document-tab {
  background: #334c79;
  color: #f4f7ff;
  border-color: #5475b0;
}
window.notepad-window.dark notebook > header tab:hover:not(:checked) .document-tab {
  background: #38465e;
  color: #ffffff;
}
"""
