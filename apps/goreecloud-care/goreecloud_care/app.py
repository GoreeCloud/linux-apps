from __future__ import annotations

import subprocess
import sys
import threading

import gi

gi.require_version("Atk", "1.0")
gi.require_version("Gtk", "3.0")
from gi.repository import Atk, Gio, GLib, Gtk  # noqa: E402

from .core import CareEngine, CategoryScan, human_bytes, read_disk_stats, read_memory_stats
from .privilege import interpret_pkexec_result
from .ui_contract import (
    COMPACT_BORDER,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    REGULAR_BORDER,
    is_compact_width,
    is_high_contrast_theme,
)

APP_ID = "com.goreecloud.care.dev"
HELPER = "/usr/lib/goreecloud-care/goreecloud-care-helper"

# Development GTK mapping of current Glaze UI V1.1 light roles. This is not a
# conformance claim; representative rendered/accessibility acceptance remains open.
CSS = b"""
window {
  background: #f5f7fa;
  color: #151a23;
}
headerbar {
  background: #ffffff;
  color: #151a23;
  border-bottom: 1px solid rgba(25, 35, 50, 0.14);
}
headerbar button { color: #151a23; }
.card {
  background: #ffffff;
  border: 1px solid rgba(25, 35, 50, 0.11);
  border-radius: 14px;
  padding: 14px;
}
.status-banner {
  background: #eef4ff;
  border: 1px solid rgba(52, 120, 246, 0.36);
  border-left-width: 4px;
  border-radius: 12px;
  padding: 11px 13px;
}
.status-banner.status-attention {
  background: #e9f6f6;
  border-color: #1c8a8d;
  box-shadow: 0 6px 18px rgba(15, 107, 111, 0.14);
}
.status-banner.status-success {
  background: #edf8f1;
  border-color: #2f9e63;
}
.status-banner.status-error {
  background: #fff0ef;
  border-color: #c63b32;
  box-shadow: 0 6px 18px rgba(198, 59, 50, 0.12);
}
.status-title {
  color: #151a23;
  font-weight: 700;
}
.status-icon { color: #3478f6; }
.status-attention .status-icon,
.status-attention .status-title { color: #0f6b6f; }
.status-success .status-icon,
.status-success .status-title { color: #2f7f53; }
.status-error .status-icon,
.status-error .status-title { color: #a92f28; }
.title { font-weight: 700; font-size: 18px; }
.muted { color: #5d6675; }
.warning { color: #b56a00; }
button.suggested-action {
  background: #1c8a8d;
  color: #ffffff;
}
button:focus, checkbutton:focus {
  outline-color: #0f6b6f;
  outline-style: solid;
  outline-width: 3px;
  outline-offset: 2px;
  box-shadow: 0 0 0 2px rgba(28, 138, 141, 0.24);
}
"""

STATUS_STYLES = ("status-info", "status-attention", "status-success", "status-error")
STATUS_ICONS = {
    "info": "dialog-information-symbolic",
    "attention": "process-stop-symbolic",
    "success": "emblem-ok-symbolic",
    "error": "dialog-error-symbolic",
}
STATUS_TITLES = {
    "info": "Status",
    "attention": "Action needs attention",
    "success": "Completed",
    "error": "Action failed",
}


class CareWindow(Gtk.ApplicationWindow):
    def __init__(self, app: Gtk.Application) -> None:
        super().__init__(application=app, title="GoreeCloud Care — Development")
        self.set_default_size(900, 680)
        self.set_size_request(MIN_WINDOW_WIDTH, MIN_WINDOW_HEIGHT)
        self.set_border_width(0)
        self.engine = CareEngine()
        self.scans: dict[str, CategoryScan] = {}
        self.rows: dict[str, tuple[Gtk.CheckButton | None, Gtk.Label]] = {}
        self.category_layouts: dict[str, tuple[Gtk.Box, Gtk.Label]] = {}
        self._compact_layout: bool | None = None

        # GoreeCloud Care intentionally opens in a light appearance by default.
        # High-contrast system themes take priority over this Development mapping.
        self.settings = Gtk.Settings.get_default()
        if self.settings is not None:
            theme_name = self.settings.get_property("gtk-theme-name")
            if not is_high_contrast_theme(theme_name):
                self.settings.set_property("gtk-application-prefer-dark-theme", False)

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_data(CSS)
        self.css_provider_attached = False
        self._sync_css_for_theme()
        if self.settings is not None:
            self.settings.connect("notify::gtk-theme-name", self._on_theme_name_changed)

        self.header_subtitle = "Development • local maintenance"
        self.header = Gtk.HeaderBar()
        self.header.set_show_close_button(True)
        self.header.props.title = "GoreeCloud Care"
        self.header.props.subtitle = self.header_subtitle
        self.set_titlebar(self.header)

        scan_btn = Gtk.Button(label="Scan")
        scan_btn.set_can_focus(True)
        scan_btn.set_tooltip_text("Scan safe maintenance categories without deleting anything")
        scan_btn.get_accessible().set_description(
            "Preview maintenance categories. Scanning does not delete files."
        )
        scan_btn.connect("clicked", self.on_scan)
        self.header.pack_end(scan_btn)

        self.root = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=14)
        self.root.set_border_width(REGULAR_BORDER)
        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        scroll.add(self.root)
        self.add(scroll)

        intro = Gtk.Label()
        intro.set_xalign(0)
        intro.set_line_wrap(True)
        intro.set_markup(
            "<span size='large' weight='bold'>Safe cleanup with a preview first</span>\n"
            "GoreeCloud Care scans local files only. It does not send telemetry. "
            "Routine cache and temporary-file cleanup runs as your user account."
        )
        self.root.pack_start(intro, False, False, 0)

        self.system_label = Gtk.Label(xalign=0)
        self.system_label.set_line_wrap(True)
        self.system_label.get_style_context().add_class("muted")
        self.root.pack_start(self.system_label, False, False, 0)

        self.status_frame = Gtk.Frame()
        self.status_frame.set_shadow_type(Gtk.ShadowType.NONE)
        self.status_frame.get_style_context().add_class("status-banner")
        self.status_frame.get_style_context().add_class("status-info")
        self.status_accessible = self.status_frame.get_accessible()
        self.status_accessible.set_role(Atk.Role.STATUSBAR)
        self.status_accessible.set_name("Ready. Scan to preview reclaimable space.")
        self.status_accessible.set_description(
            "GoreeCloud Care maintenance status and operation results."
        )

        status_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=11)
        self.status_frame.add(status_box)
        self.status_icon = Gtk.Image.new_from_icon_name(STATUS_ICONS["info"], Gtk.IconSize.BUTTON)
        self.status_icon.get_style_context().add_class("status-icon")
        status_box.pack_start(self.status_icon, False, False, 0)

        status_text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        self.status_title = Gtk.Label(xalign=0)
        self.status_title.set_line_wrap(True)
        self.status_title.get_style_context().add_class("status-title")
        self.status_title.set_text("Ready")
        status_text.pack_start(self.status_title, False, False, 0)
        self.status = Gtk.Label(xalign=0)
        self.status.set_line_wrap(True)
        self.status.set_text("Scan to preview reclaimable space.")
        status_text.pack_start(self.status, False, False, 0)
        status_box.pack_start(status_text, True, True, 0)
        self.root.pack_start(self.status_frame, False, False, 0)

        for key, title, desc, selectable in (
            ("cache", "Application cache", "Cache files older than 7 days in ~/.cache, excluding thumbnails.", True),
            ("thumbnails", "Thumbnail cache", "Recreatable image/video thumbnails stored for your account.", True),
            ("temp", "Temporary files", "Your own files in /tmp older than 7 days; symlinks are never followed.", True),
            ("trash", "Trash", "Items currently in your desktop Trash. Emptying is permanent and separately confirmed.", False),
            ("apt", "APT package cache", "Downloaded .deb package archives. Cleaning requires administrator authentication.", False),
        ):
            self.root.pack_start(self._category_card(key, title, desc, selectable), False, False, 0)

        memory = self._card()
        memory_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
        memory.add(memory_box)
        label = Gtk.Label(xalign=0)
        label.set_markup("<span weight='bold' size='large'>Memory Refresh</span>")
        memory_box.pack_start(label, False, False, 0)
        explain = Gtk.Label(xalign=0)
        explain.set_line_wrap(True)
        explain.set_text(
            "Linux intentionally uses spare RAM for file caches. Reclaiming those caches can make the "
            "available-memory number rise temporarily, but it is not a lasting speed boost and may slow "
            "the next file/app loads while caches rebuild."
        )
        explain.get_style_context().add_class("muted")
        memory_box.pack_start(explain, False, False, 0)
        memory_btn = Gtk.Button(label="Reclaim file cache…")
        memory_btn.set_can_focus(True)
        memory_btn.get_accessible().set_description(
            "Temporarily reclaim Linux file caches. Administrator authentication is required."
        )
        memory_btn.connect("clicked", self.on_reclaim_memory)
        memory_box.pack_start(memory_btn, False, False, 0)
        self.root.pack_start(memory, False, False, 0)

        self.controls = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        clean = Gtk.Button(label="Clean selected")
        clean.set_can_focus(True)
        clean.get_style_context().add_class("suggested-action")
        clean.get_accessible().set_description(
            "Clean only the selected application-cache, thumbnail-cache, and temporary-file categories."
        )
        clean.connect("clicked", self.on_clean_selected)
        self.controls.pack_start(clean, False, False, 0)

        trash = Gtk.Button(label="Empty Trash…")
        trash.set_can_focus(True)
        trash.get_accessible().set_description(
            "Permanently empty the desktop Trash after a separate confirmation."
        )
        trash.connect("clicked", self.on_empty_trash)
        self.controls.pack_start(trash, False, False, 0)

        apt = Gtk.Button(label="Clean APT cache…")
        apt.set_can_focus(True)
        apt.get_accessible().set_description(
            "Remove downloaded APT package archives after administrator authentication."
        )
        apt.connect("clicked", self.on_apt_clean)
        self.controls.pack_start(apt, False, False, 0)
        self.root.pack_start(self.controls, False, False, 0)

        self.action_buttons = (clean, trash, apt)
        self.connect("size-allocate", self._on_size_allocate)
        self._apply_layout(900)

        self.refresh_system_status()
        GLib.idle_add(lambda: (self.on_scan(None), False)[1])

    def _card(self) -> Gtk.Frame:
        frame = Gtk.Frame()
        frame.set_shadow_type(Gtk.ShadowType.NONE)
        frame.get_style_context().add_class("card")
        return frame

    def _category_card(self, key: str, title: str, desc: str, selectable: bool) -> Gtk.Widget:
        frame = self._card()
        outer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        frame.add(outer)

        body = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=12)
        outer.pack_start(body, True, True, 0)

        selector: Gtk.CheckButton | None = None
        if selectable:
            selector = Gtk.CheckButton()
            selector.set_can_focus(True)
            selector.set_active(True)
            selector.set_tooltip_text(f"Include {title.lower()} in Clean selected")
            selector.get_accessible().set_name(f"Include {title} in Clean selected")
            selector.get_accessible().set_description(desc)
            body.pack_start(selector, False, False, 0)

        text = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
        heading = Gtk.Label(xalign=0)
        heading.set_line_wrap(True)
        heading.set_markup(f"<span weight='bold' size='large'>{GLib.markup_escape_text(title)}</span>")
        text.pack_start(heading, False, False, 0)
        description = Gtk.Label(label=desc, xalign=0)
        description.set_line_wrap(True)
        description.get_style_context().add_class("muted")
        text.pack_start(description, False, False, 0)
        body.pack_start(text, True, True, 0)

        amount = Gtk.Label(label="Not scanned", xalign=1)
        amount.get_accessible().set_name(f"{title}: not scanned")
        outer.pack_end(amount, False, False, 0)

        self.rows[key] = (selector, amount)
        self.category_layouts[key] = (outer, amount)
        return frame

    def _on_size_allocate(self, _widget, allocation) -> None:
        self._apply_layout(allocation.width)

    def _apply_layout(self, width: int) -> None:
        compact = is_compact_width(width)
        if compact == self._compact_layout:
            return
        self._compact_layout = compact
        self.root.set_border_width(COMPACT_BORDER if compact else REGULAR_BORDER)
        self.header.set_subtitle(None if compact else self.header_subtitle)
        self.controls.set_orientation(
            Gtk.Orientation.VERTICAL if compact else Gtk.Orientation.HORIZONTAL
        )
        for button in self.action_buttons:
            button.set_hexpand(compact)
            button.set_halign(Gtk.Align.FILL if compact else Gtk.Align.START)
        for outer, amount in self.category_layouts.values():
            outer.set_orientation(
                Gtk.Orientation.VERTICAL if compact else Gtk.Orientation.HORIZONTAL
            )
            amount.set_xalign(0 if compact else 1)
            amount.set_halign(Gtk.Align.START if compact else Gtk.Align.END)

    def _on_theme_name_changed(self, *_args) -> None:
        self._sync_css_for_theme()

    def _sync_css_for_theme(self) -> None:
        screen = self.get_screen()
        if screen is None:
            return
        theme_name = (
            self.settings.get_property("gtk-theme-name")
            if self.settings is not None
            else None
        )
        high_contrast = is_high_contrast_theme(theme_name)
        if high_contrast and self.css_provider_attached:
            Gtk.StyleContext.remove_provider_for_screen(screen, self.css_provider)
            self.css_provider_attached = False
        elif not high_contrast and not self.css_provider_attached:
            Gtk.StyleContext.add_provider_for_screen(
                screen, self.css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
            )
            self.css_provider_attached = True
        if self.settings is not None and not high_contrast:
            self.settings.set_property("gtk-application-prefer-dark-theme", False)

    def refresh_system_status(self) -> None:
        mem = read_memory_stats()
        disk = read_disk_stats()
        self.system_label.set_text(
            f"Disk: {human_bytes(disk.free)} free of {human_bytes(disk.total)}  •  "
            f"Memory: {human_bytes(mem.available)} available of {human_bytes(mem.total)}  •  "
            f"File cache: about {human_bytes(mem.cached)}"
        )

    def set_status(self, text: str, state: str = "info", title: str | None = None) -> None:
        if state not in STATUS_ICONS:
            state = "info"
        resolved_title = title or STATUS_TITLES[state]
        context = self.status_frame.get_style_context()
        for class_name in STATUS_STYLES:
            context.remove_class(class_name)
        context.add_class(f"status-{state}")
        self.status_icon.set_from_icon_name(STATUS_ICONS[state], Gtk.IconSize.BUTTON)
        self.status_title.set_text(resolved_title)
        self.status.set_text(text)
        self.status_accessible.set_name(f"{resolved_title}. {text}")
        try:
            self.status_accessible.emit("visible-data-changed")
        except (TypeError, RuntimeError):
            pass

    def run_thread(self, fn, done) -> None:
        def worker() -> None:
            try:
                value = fn()
                GLib.idle_add(done, value, None)
            except Exception as exc:  # UI boundary: surface failure, do not claim success.
                GLib.idle_add(done, None, exc)
        threading.Thread(target=worker, daemon=True).start()

    def _apply_scans(self, scans) -> int:
        self.scans = scans
        total = 0
        for key, scan in scans.items():
            total += scan.bytes
            amount_text = f"{human_bytes(scan.bytes)} • {scan.count} items"
            self.rows[key][1].set_text(amount_text)
            self.rows[key][1].get_accessible().set_name(
                f"{scan.label}: {human_bytes(scan.bytes)}, {scan.count} items"
            )
        self.refresh_system_status()
        return total

    def on_scan(self, _button) -> None:
        self.set_status("Scanning without deleting files…", "info", "Scanning")
        self.run_thread(self.engine.scan_all, self._scan_done)

    def _scan_done(self, scans, error) -> bool:
        if error:
            self.set_status(f"Scan failed: {error}", "error", "Scan failed")
            return False
        total = self._apply_scans(scans)
        self.set_status(
            f"Up to {human_bytes(total)} is visible across all maintenance categories.",
            "info",
            "Scan complete",
        )
        return False

    def _refresh_after_action(self, text: str, state: str, title: str) -> None:
        """Refresh category/system values without overwriting the action result."""
        self.run_thread(
            self.engine.scan_all,
            lambda scans, error: self._refresh_after_action_done(scans, error, text, state, title),
        )

    def _refresh_after_action_done(self, scans, error, text: str, state: str, title: str) -> bool:
        if error:
            self.refresh_system_status()
            self.set_status(
                f"{text} Follow-up scan failed: {error}",
                "attention",
                f"{title}; refresh incomplete",
            )
            return False
        self._apply_scans(scans)
        self.set_status(text, state, title)
        return False

    def _confirm(
        self,
        primary: str,
        secondary: str,
        destructive: bool = False,
        cancel_status: str | None = None,
    ) -> bool:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING if destructive else Gtk.MessageType.QUESTION,
            buttons=Gtk.ButtonsType.CANCEL,
            text=primary,
        )
        dialog.format_secondary_text(secondary)
        label = "Delete permanently" if destructive else "Continue"
        response_id = Gtk.ResponseType.ACCEPT
        dialog.add_button(label, response_id)
        dialog.set_default_response(Gtk.ResponseType.CANCEL)
        cancel = dialog.get_widget_for_response(Gtk.ResponseType.CANCEL)
        if cancel is not None:
            cancel.grab_focus()
        response = dialog.run()
        dialog.destroy()
        accepted = response == response_id
        if not accepted and cancel_status:
            self.set_status(cancel_status, "attention", "Action cancelled")
        return accepted

    def _show_notice(self, primary: str, secondary: str, message_type=Gtk.MessageType.INFO) -> None:
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=message_type,
            buttons=Gtk.ButtonsType.CLOSE,
            text=primary,
        )
        dialog.format_secondary_text(secondary)
        dialog.run()
        dialog.destroy()

    def on_clean_selected(self, _button) -> None:
        selected: list[str] = []
        for key in ("cache", "thumbnails", "temp"):
            selector = self.rows[key][0]
            if selector is not None and selector.get_active():
                selected.append(key)
        if not selected:
            self.set_status(
                "Select at least one cache or temporary-file category.",
                "attention",
                "Selection needed",
            )
            return
        if any(key not in self.scans for key in selected):
            self.set_status("Scan first so cleanup has a current preview.", "attention", "Scan required")
            return
        total = sum(self.scans[key].bytes for key in selected)
        names = ", ".join(self.scans[key].label for key in selected)
        if not self._confirm(
            "Clean the selected categories?",
            f"About {human_bytes(total)} is currently eligible from: {names}. Files may be recreated by applications.",
            cancel_status="Selected cleanup cancelled. No cache or temporary files were changed.",
        ):
            return
        self.set_status("Cleaning selected user-owned cache and temporary files…", "info", "Cleaning")

        def action():
            return [self.engine.cleanup(self.scans[key]) for key in selected]

        self.run_thread(action, self._cleanup_done)

    def _cleanup_done(self, results, error) -> bool:
        if error:
            self.set_status(f"Cleanup failed: {error}", "error", "Cleanup failed")
            return False
        reclaimed = sum(r.reclaimed_bytes for r in results)
        failures = sum(len(r.errors) for r in results)
        msg = f"Approximately {human_bytes(reclaimed)} removed."
        if failures:
            msg += f" {failures} item(s) could not be removed; no success is claimed for those items."
            self._refresh_after_action(msg, "attention", "Cleanup finished with exceptions")
        else:
            self._refresh_after_action(msg, "success", "Cleanup complete")
        return False

    def on_empty_trash(self, _button) -> None:
        scan = self.scans.get("trash")
        amount = human_bytes(scan.bytes) if scan else "the current contents"
        if not self._confirm(
            "Permanently empty Trash?",
            f"This will permanently delete {amount} from your Trash. This action cannot be undone by GoreeCloud Care.",
            destructive=True,
            cancel_status="Trash emptying cancelled. No Trash contents were removed.",
        ):
            return
        self.set_status("Permanently emptying Trash…", "info", "Emptying Trash")
        self.run_thread(self.engine.empty_trash, self._trash_done)

    def _trash_done(self, result, error) -> bool:
        if error:
            self.set_status(f"Trash cleanup failed: {error}", "error", "Trash cleanup failed")
            return False
        msg = f"Approximately {human_bytes(result.reclaimed_bytes)} removed from Trash."
        if result.errors:
            msg += f" {len(result.errors)} item(s) were not removed."
            self._refresh_after_action(msg, "attention", "Trash cleanup finished with exceptions")
        else:
            self._refresh_after_action(msg, "success", "Trash emptied")
        return False

    def _run_privileged(self, action: str):
        return subprocess.run(
            ["/usr/bin/pkexec", HELPER, action],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            timeout=150,
            check=False,
        )

    def on_apt_clean(self, _button) -> None:
        scan = self.scans.get("apt")
        amount = human_bytes(scan.bytes) if scan else "the downloaded package cache"
        if not self._confirm(
            "Clean the APT package cache?",
            f"This removes {amount} of downloaded .deb archives when present. Administrator authentication is required.",
            cancel_status="APT cache cleanup cancelled before administrator authorization. No privileged changes were made.",
        ):
            return
        self.set_status(
            "Requesting administrator authorization for APT cache cleanup…",
            "info",
            "Authorization required",
        )
        self.run_thread(
            lambda: self._run_privileged("apt-clean"),
            lambda result, error: self._privileged_done("APT cache cleanup", result, error),
        )

    def on_reclaim_memory(self, _button) -> None:
        if not self._confirm(
            "Reclaim Linux file caches now?",
            "Linux normally manages these caches automatically. This can temporarily increase available RAM, "
            "but is not a lasting speed boost and may make later file/app loads slower while caches rebuild. "
            "Administrator authentication is required.",
            cancel_status="Memory-cache reclaim cancelled before administrator authorization. No privileged changes were made.",
        ):
            return
        self.set_status(
            "Requesting administrator authorization for memory-cache reclaim…",
            "info",
            "Authorization required",
        )
        self.run_thread(
            lambda: self._run_privileged("reclaim-memory"),
            lambda result, error: self._privileged_done("Memory-cache reclaim", result, error),
        )

    def _privileged_done(self, action_label: str, result, error) -> bool:
        if error:
            message = f"{action_label} failed before completion: {error}. No successful privileged change is claimed."
            self.set_status(message, "error", "Privileged maintenance failed")
            self._show_notice("Privileged maintenance failed", message, Gtk.MessageType.ERROR)
            return False

        outcome = interpret_pkexec_result(result.returncode, result.stderr, action_label)

        if outcome.cancelled:
            self.set_status(outcome.message, "attention", "Authorization cancelled")
            self._show_notice(
                "Administrator authorization cancelled",
                outcome.message,
                Gtk.MessageType.INFO,
            )
            return False

        if not outcome.completed:
            self.set_status(outcome.message, "error", "Privileged maintenance did not complete")
            self._show_notice(
                "Privileged maintenance did not complete",
                outcome.message,
                Gtk.MessageType.ERROR,
            )
            return False

        completion_title = f"{action_label} complete"
        self.set_status(outcome.message, "success", completion_title)
        self._show_notice(completion_title, outcome.message, Gtk.MessageType.INFO)
        self._refresh_after_action(outcome.message, "success", completion_title)
        return False


class CareApplication(Gtk.Application):
    def __init__(self) -> None:
        super().__init__(application_id=APP_ID, flags=Gio.ApplicationFlags.FLAGS_NONE)

    def do_activate(self) -> None:
        window = self.props.active_window
        if not window:
            window = CareWindow(self)
        window.show_all()
        window.present()


def main() -> int:
    app = CareApplication()
    return app.run(sys.argv)


if __name__ == "__main__":
    raise SystemExit(main())
