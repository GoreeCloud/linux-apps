from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk  # noqa: E402

from goreecloud_care.app import CareWindow
from goreecloud_care.core import Candidate, CategoryScan


def drain_events(limit: int = 500) -> None:
    count = 0
    while Gtk.events_pending() and count < limit:
        Gtk.main_iteration_do(False)
        count += 1


def wait_for_initial_scan(window: CareWindow, timeout: float = 8.0) -> None:
    """Let the constructor's read-only idle scan finish before task-flow assertions."""
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        drain_events()
        name = window.status_accessible.get_name() or ""
        if name.startswith("Scan complete.") or name.startswith("Scan complete with exceptions."):
            return
        time.sleep(0.02)
    raise AssertionError(f"initial read-only scan did not settle: {window.status_accessible.get_name()!r}")


def make_app() -> Gtk.Application:
    app = Gtk.Application(application_id=None, flags=Gio.ApplicationFlags.NON_UNIQUE)
    app.register(None)
    return app


def synthetic_scans() -> dict[str, CategoryScan]:
    return {
        "cache": CategoryScan("cache", "Application cache", [Candidate("cache", Path("/tmp/care-fake-cache"), 1024)]),
        "thumbnails": CategoryScan("thumbnails", "Thumbnail cache", [Candidate("thumbnails", Path("/tmp/care-fake-thumb"), 2048)]),
        "temp": CategoryScan("temp", "Temporary files", []),
        "trash": CategoryScan("trash", "Trash", [Candidate("trash", Path("/tmp/care-fake-trash"), 4096)]),
        "apt": CategoryScan("apt", "APT package cache", []),
    }


def _fail_if_called(label: str):
    def fail(*_args, **_kwargs):
        raise AssertionError(f"{label} was invoked across a cancellation boundary")
    return fail


def _respond_to_next_dialog(response: Gtk.ResponseType, observations: dict[str, object]) -> bool:
    for window in Gtk.Window.list_toplevels():
        if not isinstance(window, Gtk.MessageDialog) or not window.get_visible():
            continue
        observations["dialog_seen"] = True
        cancel = window.get_widget_for_response(Gtk.ResponseType.CANCEL)
        if cancel is not None:
            observations["cancel_present"] = True
            observations["cancel_focused"] = window.get_focus() is cancel
            observations["cancel_default"] = window.get_default_widget() is cancel
        window.response(response)
        return False
    return True


def cancel_confirmation(handler, *, label: str) -> None:
    observations: dict[str, object] = {}
    GLib.timeout_add(10, _respond_to_next_dialog, Gtk.ResponseType.CANCEL, observations)
    handler(None)
    # Gtk.Dialog.run() has already processed the response. Do not drain unrelated
    # idle sources here; the caller asserts the cancellation status immediately.
    assert observations.get("dialog_seen"), f"{label}: confirmation dialog did not appear"
    assert observations.get("cancel_present"), f"{label}: confirmation lacks Cancel"
    assert observations.get("cancel_focused"), f"{label}: Cancel was not initially focused"
    assert observations.get("cancel_default"), f"{label}: Cancel was not the default response"


def close_next_notice() -> dict[str, object]:
    observations: dict[str, object] = {}
    GLib.timeout_add(10, _respond_to_next_dialog, Gtk.ResponseType.CLOSE, observations)
    return observations


def test_safe_confirmation_and_cancellation_boundaries(app: Gtk.Application) -> None:
    window = CareWindow(app)
    window.show_all()
    wait_for_initial_scan(window)
    window.scans = synthetic_scans()

    # Never permit a cancellation-path regression to touch the filesystem or
    # privileged boundary in this runtime test.
    window.engine.cleanup = _fail_if_called("routine cleanup")
    window.engine.empty_trash = _fail_if_called("Trash cleanup")
    window._run_privileged = _fail_if_called("PolicyKit command")

    cancel_confirmation(window.on_clean_selected, label="Clean selected")
    assert window.status_accessible.get_name().startswith(
        "Action cancelled. Selected cleanup cancelled."
    ), window.status_accessible.get_name()

    cancel_confirmation(window.on_empty_trash, label="Empty Trash")
    assert window.status_accessible.get_name().startswith(
        "Action cancelled. Trash emptying cancelled."
    ), window.status_accessible.get_name()

    cancel_confirmation(window.on_apt_clean, label="APT cleanup")
    assert window.status_accessible.get_name().startswith(
        "Action cancelled. APT cache cleanup cancelled before administrator authorization."
    ), window.status_accessible.get_name()

    cancel_confirmation(window.on_reclaim_memory, label="Memory Refresh")
    assert window.status_accessible.get_name().startswith(
        "Action cancelled. Memory-cache reclaim cancelled before administrator authorization."
    ), window.status_accessible.get_name()

    print("Confirmation defaults and non-destructive cancellation boundaries: passed")
    window.destroy()


def test_selection_guardrails(app: Gtk.Application) -> None:
    window = CareWindow(app)
    for key in ("cache", "thumbnails", "temp"):
        selector = window.rows[key][0]
        assert selector is not None
        selector.set_active(False)
    window.on_clean_selected(None)
    assert window.status_accessible.get_name() == (
        "Selection needed. Select at least one cache or temporary-file category."
    )

    selector = window.rows["cache"][0]
    assert selector is not None
    selector.set_active(True)
    window.scans = {}
    window.on_clean_selected(None)
    assert window.status_accessible.get_name() == (
        "Scan required. Scan first so cleanup has a current preview."
    )
    print("Selection and current-preview guardrails: passed")
    window.destroy()


def test_privileged_outcome_ui_mapping(app: Gtk.Application) -> None:
    window = CareWindow(app)
    window.show_all()
    wait_for_initial_scan(window)

    # Cancellation: no success claim, explicit no-change status and notice.
    close_observation = close_next_notice()
    window._privileged_done(
        "APT cache cleanup",
        subprocess.CompletedProcess(["pkexec"], 126, "", "request dismissed"),
        None,
    )
    assert close_observation.get("dialog_seen"), "PolicyKit cancellation notice did not appear"
    assert window.status_accessible.get_name().startswith("Authorization cancelled. ")
    assert "made no privileged changes" in window.status_accessible.get_name()

    # Authorization/helper failure: remains error, never success.
    close_observation = close_next_notice()
    window._privileged_done(
        "APT cache cleanup",
        subprocess.CompletedProcess(["pkexec"], 127, "", "authorization error"),
        None,
    )
    assert close_observation.get("dialog_seen"), "PolicyKit failure notice did not appear"
    assert window.status_accessible.get_name().startswith(
        "Privileged maintenance did not complete. "
    )
    assert "No successful privileged change is claimed" in window.status_accessible.get_name()

    # A completed helper result maps to success. Stub the follow-up scan so the
    # task-flow test remains side-effect free while still exercising UI mapping.
    window._refresh_after_action = lambda text, state, title: window.set_status(text, state, title)
    close_observation = close_next_notice()
    window._privileged_done(
        "APT cache cleanup",
        subprocess.CompletedProcess(["pkexec"], 0, "", ""),
        None,
    )
    assert close_observation.get("dialog_seen"), "PolicyKit success notice did not appear"
    assert window.status_accessible.get_name() == (
        "APT cache cleanup complete. APT cache cleanup completed successfully."
    )

    print("PolicyKit success/cancellation/failure UI outcome mapping: passed")
    window.destroy()


def main() -> int:
    ok, _argv = Gtk.init_check(None)
    if not ok:
        raise SystemExit("GTK could not initialize; run this probe under Xvfb or a desktop session")
    app = make_app()
    test_selection_guardrails(app)
    test_safe_confirmation_and_cancellation_boundaries(app)
    test_privileged_outcome_ui_mapping(app)
    print("Headless GoreeCloud Care task-flow acceptance: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
