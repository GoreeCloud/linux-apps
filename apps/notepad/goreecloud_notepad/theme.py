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


STYLESHEET += """
/* Founder mockup: pale blue chrome, bold blue actions, round tabs and paper. */
window.notepad-window { background: #eef3fc; color: #111b38; }
window.notepad-window headerbar {
  background: linear-gradient(180deg, #fbfcff, #ecf3ff);
  border-bottom: 1px solid #d4e2ff;
  min-height: 67px;
  padding: 0 12px 0 16px;
}
window.notepad-window .brand-mark {
  background: #1265f5; border-radius: 11px;
  min-width: 40px; min-height: 40px; margin-right: 9px;
}
window.notepad-window .brand-mark image { color: white; -gtk-icon-size: 23px; }
window.notepad-window .toolbar-divider {
  background: #b8cefa; min-width: 1px; min-height: 27px;
  margin: 6px 10px;
}
window.notepad-window .toolbar-text-action {
  background: transparent; border: 1px solid transparent;
  box-shadow: none; color: #15213c; font-weight: 600;
  border-radius: 999px; min-height: 38px; padding: 5px 12px;
}
window.notepad-window .toolbar-text-action image { -gtk-icon-size: 19px; }
window.notepad-window .toolbar-text-action:hover { background: #e0e9fb; }
window.notepad-window .toolbar-text-action.new-action {
  background: #dce7ff; color: #005af1; font-weight: 700; padding: 5px 17px;
}
window.notepad-window .header-glyph {
  background: transparent; color: #141b30; border: none; box-shadow: none;
  border-radius: 12px; min-width: 34px; min-height: 37px;
  padding: 4px 6px; margin: 1px;
}
window.notepad-window .header-glyph:hover { background: #dce7fb; }
window.notepad-window .header-glyph.code-action {
  font-weight: 800; font-size: 15px;
}
window.notepad-window .header-glyph.preview-active {
  background: #d9e7ff; color: #0759d2;
}
window.notepad-window .header-glyph:focus-visible,
window.notepad-window .toolbar-text-action:focus-visible {
  outline: 2px solid #1265f5;
}
window.notepad-window notebook > header {
  background: #edf3ff; border: 0;
  padding: 5px 12px 3px 12px; min-height: 48px;
}
window.notepad-window notebook > header tab .document-tab {
  background: #e6efff; border: 1px solid #b8ceff;
  border-bottom: 3px solid transparent; border-radius: 999px;
  min-width: 154px; min-height: 31px; padding: 5px 10px 3px 12px;
  color: #2d4567; font-weight: 600;
}
window.notepad-window notebook > header tab:checked .document-tab {
  background: #dce8ff; border-color: #a9c7ff;
  border-bottom-color: #1265f5; color: #0059df; font-weight: 700;
}
window.notepad-window notebook > header tab .document-tab image { color: #1265f5; }
window.notepad-window notebook > header tab .tab-close {
  background: transparent; color: inherit; border-radius: 999px;
}
window.notepad-window .paper-pane {
  background: #ffffff; border: 1px solid #b8ceff; border-radius: 19px;
  box-shadow: 0 7px 22px rgba(30, 66, 130, 0.09);
}
window.notepad-window .editor-pane,
window.notepad-window textview.notepad-editor,
window.notepad-window textview.notepad-editor text,
window.notepad-window textview.notepad-preview,
window.notepad-window textview.notepad-preview text {
  background: #ffffff; color: #1b2742; caret-color: #1265f5;
}
window.notepad-window .notepad-footer {
  background: #edf3ff; border-top: 1px solid #d2e0fb;
  min-height: 45px;
}
window.notepad-window .footer-label { color: #23304b; font-size: 12px; }
window.notepad-window .save-state.saved,
window.notepad-window .save-state.saved label,
window.notepad-window .save-state.saved image { color: #07852e; font-weight: 700; }
window.notepad-window .save-state.unsaved,
window.notepad-window .save-state.unsaved label,
window.notepad-window .save-state.unsaved image { color: #98610c; font-weight: 700; }
window.notepad-window.dark { background: #121c30; color: #f0f5ff; }
window.notepad-window.dark headerbar {
  background: #202d46; border-bottom-color: #354b73;
}
window.notepad-window.dark .toolbar-divider { background: #465c80; }
window.notepad-window.dark .toolbar-text-action { color: #edf3ff; }
window.notepad-window.dark .toolbar-text-action.new-action {
  color: #b5d0ff; background: #294875;
}
window.notepad-window.dark .toolbar-text-action:hover,
window.notepad-window.dark .header-glyph:hover { background: #31476b; }
window.notepad-window.dark .header-glyph { color: #edf3ff; }
window.notepad-window.dark notebook > header { background: #18263d; }
window.notepad-window.dark notebook > header tab .document-tab {
  background: #263852; color: #d3e3ff; border-color: #425b82;
}
window.notepad-window.dark notebook > header tab:checked .document-tab {
  background: #284d83; color: #ffffff;
  border-color: #6b98e0; border-bottom-color: #74a7ff;
}
window.notepad-window.dark .paper-pane {
  background: #19253b; border-color: #425b82;
}
window.notepad-window.dark .editor-pane,
window.notepad-window.dark textview.notepad-editor,
window.notepad-window.dark textview.notepad-editor text,
window.notepad-window.dark textview.notepad-preview,
window.notepad-window.dark textview.notepad-preview text {
  background: #19253b; color: #f4f7ff; caret-color: #a8c8ff;
}
window.notepad-window.dark .notepad-footer {
  background: #202d46; border-top-color: #405474;
}
window.notepad-window.dark .footer-label { color: #e1ebff; }
window.notepad-window.dark .save-state.saved,
window.notepad-window.dark .save-state.saved label,
window.notepad-window.dark .save-state.saved image { color: #7ce89e; }
"""


STYLESHEET += """
/* Screenshot-based contrast corrections for the founder's interface mockup. */
window.notepad-window.dark .toolbar-text-action.new-action {
  background-color: #115ec9;
  color: #ffffff;
  font-weight: 700;
}
window.notepad-window.dark .toolbar-text-action.new-action image,
window.notepad-window.dark .toolbar-text-action.new-action label {
  color: #ffffff;
}
window.notepad-window.dark .toolbar-text-action.new-action:hover {
  background-color: #2275e6;
}
window.notepad-window.dark .save-state.unsaved,
window.notepad-window.dark .save-state.unsaved label,
window.notepad-window.dark .save-state.unsaved image {
  color: #ffd38a;
  font-weight: 700;
}
window.notepad-window.dark notebook > header tab:checked .tab-close,
window.notepad-window.dark notebook > header tab .document-tab image {
  color: #dbeaff;
}
window.notepad-window.dark notebook > header tab .tab-add {
  color: #ffffff;
  background-color: #345587;
  border-color: #5f7eaf;
}
window.notepad-window .toolbar-scroller {
  background: transparent;
  border: 0;
}
"""

STYLESHEET += """
/* Lossless native checkbox and horizontal-rule decorations in source view. */
window.notepad-window textview.notepad-editor checkbutton.inline-task-check {
  padding: 0; margin: 0; min-width: 35px; min-height: 24px;
  background: transparent; border: 0;
}
window.notepad-window textview.notepad-editor checkbutton.inline-task-check check {
  min-width: 19px; min-height: 19px;
  border: 2px solid #5f6c85; border-radius: 5px;
  background-color: #ffffff;
}
window.notepad-window textview.notepad-editor checkbutton.inline-task-check:checked check {
  background-color: #1265f5; border-color: #1265f5; color: #ffffff;
}
window.notepad-window textview.notepad-editor checkbutton.inline-task-check:focus-visible {
  outline: 2px solid #1265f5; outline-offset: 1px;
}
window.notepad-window textview.notepad-editor separator.inline-rule {
  background-color: #a8c6fc; min-height: 2px;
}
window.notepad-window.dark textview.notepad-editor checkbutton.inline-task-check check {
  background-color: #19253b; border-color: #aec2e7;
}
window.notepad-window.dark textview.notepad-editor checkbutton.inline-task-check:checked check {
  background-color: #4489ff; border-color: #4489ff;
}
window.notepad-window.dark textview.notepad-editor separator.inline-rule {
  background-color: #5d80b7;
}
"""
