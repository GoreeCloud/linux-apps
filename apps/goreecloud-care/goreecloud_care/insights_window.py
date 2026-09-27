from __future__ import annotations

import sys
import threading

import gi

gi.require_version("Atk", "1.0")
gi.require_version("Gtk", "3.0")
gi.require_version("Pango", "1.0")
from gi.repository import Atk, Gio, GLib, Gtk, Pango  # noqa: E402

from .insights import InsightsSnapshot, build_insights, render_insights_text
from .ui_contract import (
    COMPACT_BORDER,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    REGULAR_BORDER,
    is_compact_width,
)

APP_ID = "com.goreecloud.care.insights"
RESULTS_MIN_HEIGHT = 320
REGULAR_SPACING = 12
COMPACT_SPACING = 8
RESULTS_MARGIN = 12


class InsightsWindow(Gtk.ApplicationWindow):
    """Read-only GoreeCloud Care maintenance review surface."""

    def __init__(self, app: Gtk.Application) -> None:
        super().__init__(application=app, title="GoreeCloud Care — Maintenance Insights")
        self.set_default_size(860, 660)
        self.set_size_request(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self._compact_layout: bool | None = None

        self.header_subtitle = "Read-only local review"
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.props.title = "Maintenance Insights"
        self.header.props.subtitle = self.header_subtitle
        self.header.get_style_context().add_class("chrome-plane")
        self.set_titlebar(self.header)

        self.refresh = Gtk.Button()
        self.refresh.get_style_context().add_class("command-capsule")
        self.refresh_icon = Gtk.Image.new_from_icon_name(
            "view-refresh-symbolic", Gtk.IconSize.BUTTON
        )
        self.refresh.add(self.refresh_icon)
        self.refresh.set_can_focus(True)
        self.refresh.set_tooltip_text("Refresh read-only maintenance insights")
        self.refresh.get_accessible().set_name("Refresh")
        self.refresh.get_accessible().set_description(
            "Re-scan local maintenance insights. Refreshing does not delete files or perform maintenance."
        )
        self.refresh.connect("clicked", self.on_refresh)
        self.header.pack_end(self.refresh)

        # The entire page remains vertically reachable at enlarged text.
        self.page_scroll = Gtk.ScrolledWindow()
        self.page_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.page_scroll.set_hexpand(True)
        self.page_scroll.set_vexpand(True)
        self.add(self.page_scroll)

        self.root = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL, spacing=REGULAR_SPACING
        )
        self.root.set_border_width(REGULAR_BORDER)
        self.page_scroll.add(self.root)

        # One quiet signature summary introduces the review task. Findings remain
        # on an opaque content plane because users read and judge file paths here.
        self.summary = Gtk.Frame()
        self.summary.set_shadow_type(Gtk.ShadowType.NONE)
        self.summary.get_style_context().add_class("hero-surface")
        summary_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=6)
        self.summary.add(summary_box)

        eyebrow = Gtk.Label(xalign=0)
        eyebrow.set_text("READ-ONLY REVIEW • LOCAL ONLY")
        eyebrow.get_style_context().add_class("eyebrow")
        summary_box.pack_start(eyebrow, False, False, 0)

        self.intro_regular_markup = (
            "<span size='x-large' weight='bold'>See storage pressure before deciding what to do.</span>\n"
            "Maintenance Insights highlights stale application-cache groups, large files in standard user folders, "
            "and older Downloads. Nothing is selected or deleted automatically."
        )
        self.intro_compact_markup = (
            "<span weight='bold'>Review storage safely</span>\n"
            "Read-only. Nothing is selected or deleted automatically."
        )
        self.intro = Gtk.Label(xalign=0)
        self.intro.set_line_wrap(True)
        self.intro.set_markup(self.intro_regular_markup)
        summary_box.pack_start(self.intro, False, False, 0)

        self.privacy_regular_text = (
            "No telemetry • no network • no administrator authentication. "
            "Paths are shown only inside this local review view; default Care reports remain path-redacted."
        )
        self.privacy_compact_text = (
            "No network or telemetry • no administrator authentication • paths shown only here."
        )
        self.privacy = Gtk.Label(xalign=0)
        self.privacy.set_line_wrap(True)
        self.privacy.set_text(self.privacy_regular_text)
        self.privacy.get_style_context().add_class("muted")
        summary_box.pack_start(self.privacy, False, False, 0)
        self.root.pack_start(self.summary, False, False, 0)

        self.status_frame = Gtk.Frame()
        self.status_frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.status_frame.get_style_context().add_class("status-banner")
        self.status_frame.get_style_context().add_class("status-info")
        self.status_accessible = self.status_frame.get_accessible()
        self.status_accessible.set_role(Atk.Role.STATUSBAR)
        self.status_accessible.set_description(
            "GoreeCloud Care Maintenance Insights read-only scan status."
        )
        self.root.pack_start(self.status_frame, False, False, 0)

        self.status = Gtk.Label(xalign=0)
        self.status.set_line_wrap(True)
        self.status_frame.add(self.status)
        self._set_status("Ready to analyze local maintenance insights.")

        self.findings_plane = Gtk.Frame()
        self.findings_plane.set_shadow_type(Gtk.ShadowType.NONE)
        self.findings_plane.get_style_context().add_class("findings-plane")
        findings_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.findings_plane.add(findings_box)
        findings_title = Gtk.Label(xalign=0)
        findings_title.set_text("Findings")
        findings_title.set_margin_start(RESULTS_MARGIN)
        findings_title.set_margin_end(RESULTS_MARGIN)
        findings_title.set_margin_top(RESULTS_MARGIN)
        findings_title.set_margin_bottom(6)
        findings_title.get_style_context().add_class("section-title")
        findings_box.pack_start(findings_title, False, False, 0)

        # Findings keep their own scroll position and guaranteed visible viewport.
        self.results_scroll = Gtk.ScrolledWindow()
        self.results_scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.results_scroll.set_hexpand(True)
        self.results_scroll.set_vexpand(True)
        self.results_scroll.set_min_content_height(RESULTS_MIN_HEIGHT)
        findings_box.pack_start(self.results_scroll, True, True, 0)
        self.root.pack_start(self.findings_plane, True, True, 0)

        # Preserve dev17's accepted copy integrity: selectable Pango text uses
        # WORD_CHAR fallback with synthetic hyphen insertion disabled.
        self.results = Gtk.Label(xalign=0, yalign=0)
        self.results.set_selectable(True)
        self.results.set_line_wrap(True)
        self.results.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
        self.results.set_margin_start(RESULTS_MARGIN)
        self.results.set_margin_end(RESULTS_MARGIN)
        self.results.set_margin_top(4)
        self.results.set_margin_bottom(RESULTS_MARGIN)
        self.results.get_accessible().set_name("Maintenance Insights results")
        self.results.get_accessible().set_description(
            "Read-only maintenance findings. Review manually; nothing in this view is selected for deletion."
        )
        self.results_scroll.add(self.results)

        self.connect("size-allocate", self._on_size_allocate)
        self._apply_layout(860)
        GLib.idle_add(lambda: (self.on_refresh(None), False)[1])

    def _on_size_allocate(self, _widget, allocation) -> None:
        self._apply_layout(allocation.width)

    def _apply_layout(self, width: int) -> None:
        compact = is_compact_width(width)
        if compact == self._compact_layout:
            return
        self._compact_layout = compact
        self.root.set_border_width(COMPACT_BORDER if compact else REGULAR_BORDER)
        self.root.set_spacing(COMPACT_SPACING if compact else REGULAR_SPACING)
        self.header.set_title("Insights" if compact else "Maintenance Insights")
        self.header.set_subtitle(None if compact else self.header_subtitle)
        self.intro.set_markup(
            self.intro_compact_markup if compact else self.intro_regular_markup
        )
        self.privacy.set_text(
            self.privacy_compact_text if compact else self.privacy_regular_text
        )

    def _set_status(self, text: str) -> None:
        self.status.set_text(text)
        self.status_accessible.set_name(text)
        try:
            self.status_accessible.emit("visible-data-changed")
        except (TypeError, RuntimeError):
            pass

    def _set_results_text(self, text: str) -> None:
        escaped = GLib.markup_escape_text(text)
        self.results.set_markup(
            f"<span insert_hyphens='false'>{escaped}</span>"
        )

    def _run_thread(self, fn, done) -> None:
        def worker() -> None:
            try:
                value = fn()
                GLib.idle_add(done, value, None)
            except Exception as exc:
                GLib.idle_add(done, None, exc)

        threading.Thread(target=worker, daemon=True).start()

    def on_refresh(self, _button) -> None:
        if self._compact_layout:
            self._set_status("Refreshing read-only insights…")
        else:
            self._set_status(
                "Analyzing standard user folders and stale application cache without deleting files…"
            )
        self._run_thread(build_insights, self._refresh_done)

    def _refresh_done(self, snapshot: InsightsSnapshot | None, error: Exception | None) -> bool:
        if error is not None or snapshot is None:
            message = f"Maintenance Insights scan failed: {error}"
            self._set_status(message)
            self._set_results_text(
                message + "\nNo maintenance action was performed and no files were changed."
            )
            return False

        self._set_results_text(render_insights_text(snapshot))
        total_findings = len(snapshot.cache_groups) + len(snapshot.large_files) + len(snapshot.stale_downloads)
        if self._compact_layout:
            suffix = (
                " Partial results: discovery limit reached." if snapshot.truncated else ""
            )
            self._set_status(
                f"Ready. {total_findings} review item/group(s); "
                f"{snapshot.scan_error_count} scan error(s). No files changed.{suffix}"
            )
        else:
            suffix = " Results are partial because the bounded discovery limit was reached." if snapshot.truncated else ""
            self._set_status(
                f"Insights ready. {total_findings} review item/group(s) shown; "
                f"{snapshot.scan_error_count} scan error(s). No files were changed.{suffix}"
            )
        return False


class InsightsApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self) -> None:
        window = self.props.active_window
        if not window:
            window = InsightsWindow(self)
        window.show_all()
        window.present()


def main() -> int:
    app = InsightsApplication()
    return app.run([sys.argv[0]])
