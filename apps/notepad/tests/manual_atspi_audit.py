"""Manual out-of-process AT-SPI audit on an authorized Linux desktop.

Run: /usr/bin/python3 tests/manual_atspi_audit.py
Needs a running graphical session's DBUS_SESSION_BUS_ADDRESS, xvfb-run, GTK4,
and gir1.2-atspi-2.0. Never writes the real user's note files or preferences.

This is a programmatic assistive-technology tree check, not a substitute
for an actual screen-reader user acceptance session.
"""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

HERE = Path(__file__).resolve()
SAMPLE = "Accessible test note\n- [ ] First task\n- [x] Second task\n---\n"
NAMES = ("Task, line 2: First task", "Task, line 3: Second task")


def fixture(marker: Path) -> None:
    import gi
    gi.require_version("Gtk", "4.0")
    from gi.repository import Gio, GLib, Gtk
    from goreecloud_notepad.app import NotepadApplication

    app = NotepadApplication()
    app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
    app.register()
    app.activate()
    page = app.window.current()
    page.buffer.set_text(SAMPLE)
    app.window.present()
    context = GLib.MainContext.default()
    for _ in range(100):
        if not context.pending():
            break
        context.iteration(False)
    checks = [w for w in page.inline.widgets if isinstance(w, Gtk.CheckButton)]
    if len(checks) != 2:
        raise AssertionError(f"Expected two native checkboxes, got {len(checks)}")
    marker.write_text(str(os.getpid()), encoding="utf-8")
    loop = GLib.MainLoop()
    stop = marker.with_suffix(".stop")

    def check_stop():
        if stop.exists():
            loop.quit()
            return GLib.SOURCE_REMOVE
        return GLib.SOURCE_CONTINUE

    GLib.timeout_add(120, check_stop)
    GLib.timeout_add(14000, lambda: (loop.quit(), GLib.SOURCE_REMOVE)[1])
    loop.run()
    assert page.note.text == SAMPLE, "AT-SPI read audit must not modify the note"
    app.window._close_confirmed = True
    app.window.close()
    app.quit()


def scan_application(app):
    """Collect only relevant controls; tolerate unrelated stale AT-SPI nodes."""
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi, GLib

    pending = [(app, 0)]
    found_editor = False
    checkboxes = {}
    visited = 0
    while pending and visited < 500:
        node, depth = pending.pop()
        visited += 1
        try:
            name = node.get_name() or ""
            role = node.get_role_name()
            if name == "Note editor" and role == "text":
                found_editor = True
            if name in NAMES and role == "check box":
                states = node.get_state_set()
                checkboxes[name] = {
                    "checked": states.contains(Atspi.StateType.CHECKED),
                    "focusable": states.contains(Atspi.StateType.FOCUSABLE),
                    "description": node.get_description() or "",
                    "actions": [node.get_action_name(i)
                                for i in range(node.get_n_actions())],
                }
            if depth < 15:
                for i in range(min(node.get_child_count(), 70) - 1, -1, -1):
                    child = node.get_child_at_index(i)
                    if child is not None:
                        pending.append((child, depth + 1))
        except (GLib.Error, RuntimeError, AttributeError):
            continue
    return found_editor, checkboxes


def inspect_external(pid: int) -> None:
    import gi
    gi.require_version("Atspi", "2.0")
    from gi.repository import Atspi, GLib

    deadline = time.monotonic() + 8.0
    while time.monotonic() < deadline:
        desktop = Atspi.get_desktop(0)
        for i in range(min(desktop.get_child_count(), 60)):
            try:
                application = desktop.get_child_at_index(i)
                if application is None or application.get_process_id() != pid:
                    continue
                editor, checks = scan_application(application)
                if editor and len(checks) == 2:
                    first, second = (checks[name] for name in NAMES)
                    assert first["focusable"] and second["focusable"]
                    assert not first["checked"] and second["checked"]
                    assert all("Space" in data["description"]
                               and "Ctrl+Enter" in data["description"]
                               for data in (first, second))
                    print("External AT-SPI editor text role: PASS", flush=True)
                    print("External AT-SPI checkbox names, states, and descriptions: PASS", flush=True)
                    print("Checkbox AT-SPI actions:", first["actions"], flush=True)
                    return
            except (GLib.Error, RuntimeError, AttributeError):
                continue
        time.sleep(0.2)
    raise AssertionError("Notepad AT-SPI tree not found on this desktop bus")


def run() -> None:
    if not os.environ.get("DBUS_SESSION_BUS_ADDRESS"):
        raise RuntimeError("A running desktop session accessibility bus is required")
    with tempfile.TemporaryDirectory(prefix="gcn-manual-atspi-") as folder:
        private = Path(folder)
        marker = private / "ready"
        env = os.environ.copy()
        env.update(
            XDG_CONFIG_HOME=str(private / "config"),
            GTK_A11Y="atspi",
            GDK_BACKEND="x11",
            PYTHONPATH=str(HERE.parents[1]),
        )
        app = subprocess.Popen(
            ["xvfb-run", "-a", "/usr/bin/python3", str(HERE), "--fixture", str(marker)],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env,
        )
        try:
            deadline = time.monotonic() + 9
            while not marker.exists() and time.monotonic() < deadline:
                if app.poll() is not None:
                    out, err = app.communicate()
                    raise RuntimeError(f"GTK fixture exited: {out} {err[-1000:]}")
                time.sleep(0.2)
            if not marker.exists():
                raise TimeoutError("GTK fixture did not start")
            fixture_pid = int(marker.read_text(encoding="utf-8"))
            result = subprocess.run(
                ["/usr/bin/python3", str(HERE), "--client", str(fixture_pid)],
                capture_output=True, text=True, env=env, timeout=12,
            )
            if result.returncode:
                raise AssertionError(result.stdout + result.stderr[-1200:])
            print(result.stdout, end="")
        finally:
            if marker.exists():
                marker.with_suffix(".stop").write_text("done", encoding="utf-8")
            try:
                _stdout, stderr = app.communicate(timeout=4)
            except subprocess.TimeoutExpired:
                app.terminate()
                try:
                    _stdout, stderr = app.communicate(timeout=2)
                except subprocess.TimeoutExpired:
                    app.kill()
                    _stdout, stderr = app.communicate()
            if app.returncode and not sys.exc_info()[0]:
                raise RuntimeError(f"GTK fixture failed: {stderr[-1200:]}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--fixture":
        fixture(Path(sys.argv[2]))
    elif len(sys.argv) > 2 and sys.argv[1] == "--client":
        inspect_external(int(sys.argv[2]))
    else:
        run()
