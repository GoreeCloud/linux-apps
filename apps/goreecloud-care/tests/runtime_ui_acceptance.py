from __future__ import annotations

import os
import sys
import time
from pathlib import Path

os.environ.setdefault("GDK_DPI_SCALE", "2")

# This file is intentionally runnable both from the repository root and directly
# from tests/. Python otherwise puts tests/ rather than the Care source root on
# sys.path when invoked as `python3 tests/runtime_ui_acceptance.py`.
SOURCE_ROOT = Path(__file__).resolve().parents[1]
if str(SOURCE_ROOT) not in sys.path:
    sys.path.insert(0, str(SOURCE_ROOT))

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, Gtk  # noqa: E402

from goreecloud_care.app import CareWindow
from goreecloud_care.glaze_v13 import (
    CSS,
    GLAZE_UI_CONSUMER_ELIGIBLE,
    GLAZE_UI_LIFECYCLE,
    GLAZE_UI_STABLE_BASELINE,
    GLAZE_UI_TARGET_VERSION,
)
from goreecloud_care.glaze_v13_global import install_glaze_v13_global_style
from goreecloud_care.insights import CacheGroupInsight, FileInsight, InsightsSnapshot
import goreecloud_care.insights_window as insights_window


def drain_events(limit: int = 500) -> None:
    count = 0
    while Gtk.events_pending() and count < limit:
        Gtk.main_iteration_do(False)
        count += 1


def make_app() -> Gtk.Application:
    # No application ID means the headless CI probe does not require a session
    # D-Bus name. NON_UNIQUE keeps the test isolated from desktop registration.
    app = Gtk.Application(
        application_id=None,
        flags=Gio.ApplicationFlags.NON_UNIQUE,
    )
    app.register(None)
    return app


def _truthy(value: str | None) -> bool:
    return (value or "").strip().lower() in {"1", "true", "yes", "on"}


def _linear_channel(value: float) -> float:
    if value <= 0.04045:
        return value / 12.92
    return ((value + 0.055) / 1.055) ** 2.4


def _relative_luminance(rgba) -> float:
    red = _linear_channel(float(rgba.red))
    green = _linear_channel(float(rgba.green))
    blue = _linear_channel(float(rgba.blue))
    return 0.2126 * red + 0.7152 * green + 0.0722 * blue


def _contrast_ratio(foreground, background) -> float:
    first = _relative_luminance(foreground)
    second = _relative_luminance(background)
    lighter, darker = max(first, second), min(first, second)
    return (lighter + 0.05) / (darker + 0.05)


def _descendant_buttons(widget) -> list[Gtk.Button]:
    found: list[Gtk.Button] = []
    if isinstance(widget, Gtk.Button):
        found.append(widget)
    if isinstance(widget, Gtk.Container):
        for child in widget.get_children():
            found.extend(_descendant_buttons(child))
    return found


def test_core_status_accessible_mutation_and_layout(app: Gtk.Application) -> None:
    window = CareWindow(app)
    visible_data_events: list[str] = []
    window.status_accessible.connect(
        "visible-data-changed",
        lambda accessible: visible_data_events.append(accessible.get_name() or ""),
    )
    # set_status emits visible-data-changed synchronously. Assert before draining
    # the constructor's idle initial-scan source, which intentionally updates the
    # same status surface afterward.
    window.set_status("Synthetic completion state.", "success", "Completed")
    name = window.status_accessible.get_name()
    assert name == "Completed. Synthetic completion state.", name
    assert visible_data_events, "status accessible did not emit visible-data-changed"
    assert visible_data_events[-1] == name, visible_data_events[-1]

    window._apply_layout(480)
    assert window._layout_environment == "compact"
    assert window.header.get_title() == "Care"
    assert window.header.get_subtitle() is None
    assert window.workspace.get_orientation() == Gtk.Orientation.VERTICAL
    window._apply_layout(1800)
    assert window._layout_environment == "medium"
    assert window.header.get_title() == "GoreeCloud Care"
    assert window.header.get_subtitle() == window.header_subtitle
    assert window.workspace.get_orientation() == Gtk.Orientation.VERTICAL
    window._apply_layout(2200)
    assert window._layout_environment == "expanded"
    assert window.header.get_title() == "GoreeCloud Care"
    assert window.workspace.get_orientation() == Gtk.Orientation.HORIZONTAL
    window.destroy()


def test_dark_headerbar_runtime_contrast(app: Gtk.Application) -> None:
    appearance = os.environ.get("GOREECLOUD_CARE_APPEARANCE", "").strip().lower()
    if appearance not in {"dark", "deep-dark"}:
        return

    window = CareWindow(app)
    window.show_all()
    drain_events()

    buttons = [button for button in _descendant_buttons(window.header) if button.get_visible()]
    assert window.scan_btn in buttons, "Scan button is missing from the realized HeaderBar"
    assert buttons, "No visible HeaderBar buttons were realized"

    checked = 0
    for button in buttons:
        context = button.get_style_context()
        state = context.get_state()
        foreground = context.get_color(state)
        background = context.get_background_color(state)
        # Dev22 deliberately makes Dark/Deep Dark HeaderBar button surfaces
        # opaque. If the cascade falls back to a transparent/light theme surface,
        # fail instead of treating source CSS as sufficient evidence.
        assert background.alpha >= 0.95, (
            f"{appearance} HeaderBar button background alpha is {background.alpha:.3f}"
        )
        ratio = _contrast_ratio(foreground, background)
        assert ratio >= 4.5, (
            f"{appearance} HeaderBar button contrast is only {ratio:.2f}:1 "
            f"(fg={foreground.to_string()}, bg={background.to_string()})"
        )
        checked += 1

    print(f"{appearance} HeaderBar runtime contrast: passed for {checked} visible button(s)")
    window.destroy()


def test_clarity_runtime_geometry(app: Gtk.Application) -> None:
    clarity = os.environ.get("GOREECLOUD_CARE_GLAZE_CLARITY", "").strip().lower()
    if clarity not in {"clear", "balanced", "dense"}:
        return

    window = CareWindow(app)
    window.show_all()
    drain_events()

    row = window.category_layouts["cache"][0]
    context = row.get_style_context()
    padding = context.get_padding(context.get_state())
    expected = {
        "clear": (15, 16),
        "balanced": (12, 14),
        "dense": (9, 12),
    }[clarity]
    vertical, horizontal = expected
    assert (padding.top, padding.bottom) == (vertical, vertical), (
        clarity,
        padding.top,
        padding.bottom,
    )
    assert (padding.left, padding.right) == (horizontal, horizontal), (
        clarity,
        padding.left,
        padding.right,
    )
    assert window.clean.get_can_focus()
    assert window.trash.get_can_focus()
    assert window.apt.get_can_focus()
    assert window.memory_btn.get_can_focus()

    print(
        f"{clarity} clarity runtime geometry: passed "
        f"(vertical={vertical}px, horizontal={horizontal}px)"
    )
    window.destroy()


def test_reduced_motion_runtime_contract(app: Gtk.Application) -> None:
    if not _truthy(os.environ.get("GOREECLOUD_CARE_REDUCE_MOTION")):
        return

    # Care currently owns no timed animation or transition. Reduced Motion also
    # suppresses the only application-owned expressive hover/elevation effect.
    # This makes the gate deterministic instead of relying on a screenshot.
    css = CSS.decode("utf-8")
    assert "transition:" not in css
    assert "animation:" not in css
    assert (
        "window.care-shell.reduced-motion button:hover,\n"
        "window.care-shell.reduced-motion .hero-surface { box-shadow: none; }"
    ) in css

    window = CareWindow(app)
    window.show_all()
    drain_events()
    assert window.scan_btn.get_can_focus()
    assert window.clean.get_can_focus()
    print("Reduced Motion application-owned behavior: passed (no timed motion; elevation suppressed)")
    window.destroy()


def test_insights_focus_resize_and_rendering(app: Gtk.Application) -> None:
    snapshot = InsightsSnapshot(
        cache_groups=(CacheGroupInsight("example-cache", 1024, 2),),
        large_files=(
            FileInsight(
                "~/Pictures/a-very-long-path-component-without-synthetic-hyphenation/example-video.mp4",
                512 * 1024 * 1024,
                35,
            ),
        ),
        stale_downloads=(),
        scan_error_count=0,
        visited_entries=42,
        truncated=False,
    )
    insights_window.build_insights = lambda: snapshot

    window = insights_window.InsightsWindow(app)
    window.show_all()
    drain_events()

    window._set_results_text(insights_window.render_insights_text(snapshot))
    assert window.results.get_selectable()
    assert window.results.get_can_focus()
    assert "example-video.mp4" in window.results.get_text()
    assert "synthetic-hyphenation" in window.results.get_text()
    assert window.findings_plane.get_style_context().has_class("findings-plane")
    assert window.refresh.get_style_context().has_class("command-capsule")

    # At GDK_DPI_SCALE=2 the effective layout width is half the allocated width.
    window._apply_layout(480)
    assert window.header.get_title() == "Insights"
    assert window.header.get_subtitle() is None
    window._apply_layout(1800)
    assert window.header.get_title() == "Maintenance Insights"
    assert window.header.get_subtitle() == window.header_subtitle

    window.refresh.grab_focus()
    drain_events()
    assert window.get_focus() is window.refresh
    moved_forward = window.child_focus(Gtk.DirectionType.TAB_FORWARD)
    drain_events()
    assert moved_forward
    assert window.get_focus() is window.results, type(window.get_focus()).__name__

    moved_backward = window.child_focus(Gtk.DirectionType.TAB_BACKWARD)
    drain_events()
    assert moved_backward
    assert window.get_focus() is window.refresh, type(window.get_focus()).__name__

    start = time.monotonic()
    for _ in range(20):
        window.resize(480, 620)
        drain_events()
        window.resize(1800, 720)
        drain_events()
    elapsed = time.monotonic() - start
    assert elapsed < 5.0, f"synthetic continuous resize took {elapsed:.3f}s"

    window.destroy()


def main() -> int:
    ok, _argv = Gtk.init_check(None)
    if not ok:
        raise SystemExit("GTK could not initialize; run this probe under Xvfb or a desktop session")

    glaze = install_glaze_v13_global_style()
    assert GLAZE_UI_TARGET_VERSION == "1.3.0-candidate"
    assert GLAZE_UI_LIFECYCLE == "proposed"
    assert GLAZE_UI_STABLE_BASELINE == "1.2.0"
    assert not GLAZE_UI_CONSUMER_ELIGIBLE
    assert glaze.provider_attached, "Proposed GLAZE UI V1.3 provider was not attached"

    app = make_app()
    test_core_status_accessible_mutation_and_layout(app)
    test_dark_headerbar_runtime_contrast(app)
    test_clarity_runtime_geometry(app)
    test_reduced_motion_runtime_contract(app)
    test_insights_focus_resize_and_rendering(app)
    print(
        "Headless GTK runtime acceptance probe: passed "
        "(Proposed GLAZE UI V1.3 Adaptive Resonance Development mapping; V1.2 Stable baseline retained)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
