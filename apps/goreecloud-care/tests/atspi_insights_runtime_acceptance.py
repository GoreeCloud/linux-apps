from __future__ import annotations

import threading
import time

import pyatspi

APP_NAME = "GoreeCloud Care"
STATUS_EVENT_TYPES = (
    "object:visible-data-changed",
    "object:property-change:accessible-name",
)


def _name(accessible) -> str:
    try:
        return accessible.name or ""
    except Exception:
        return ""


def _role(accessible):
    try:
        return accessible.getRole()
    except Exception:
        return None


def _children(accessible):
    try:
        count = accessible.childCount
    except Exception:
        return
    for index in range(count):
        try:
            child = accessible.getChildAtIndex(index)
        except Exception:
            continue
        if child is not None:
            yield child


def _walk(accessible, *, max_depth: int = 24, depth: int = 0):
    if accessible is None or depth > max_depth:
        return
    yield accessible
    for child in _children(accessible):
        yield from _walk(child, max_depth=max_depth, depth=depth + 1)


def _wait_for_insights_application(timeout: float = 12.0):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        desktop = pyatspi.Registry.getDesktop(0)
        for child in _children(desktop):
            if _name(child) != APP_NAME:
                continue
            # Distinguish the dedicated Insights process from the core Care UI by
            # its explicitly named Refresh action.
            if _find(child, role=pyatspi.ROLE_PUSH_BUTTON, name="Refresh") is not None:
                return child
        time.sleep(0.1)
    raise AssertionError("Maintenance Insights AT-SPI application was not discovered")


def _find(accessible, *, role=None, name: str | None = None):
    for node in _walk(accessible):
        if role is not None and _role(node) != role:
            continue
        if name is not None and _name(node) != name:
            continue
        return node
    return None


def _invoke(button) -> None:
    action = button.queryAction()
    assert action.nActions > 0, f"{_name(button)} exposes no AT-SPI action"
    chosen = 0
    for index in range(action.nActions):
        action_name = (action.getName(index) or "").lower()
        if action_name in {"click", "press", "activate"}:
            chosen = index
            break
    assert action.doAction(chosen), f"AT-SPI action invocation failed for {_name(button)}"


def main() -> int:
    app = _wait_for_insights_application()
    assert _role(app) == pyatspi.ROLE_APPLICATION, (
        f"unexpected root role {_role(app)!r} for {_name(app)!r}"
    )

    refresh = _find(app, role=pyatspi.ROLE_PUSH_BUTTON, name="Refresh")
    assert refresh is not None, "Refresh was not exposed over AT-SPI"
    status = _find(app, role=pyatspi.ROLE_STATUS_BAR)
    assert status is not None, "Maintenance Insights STATUS_BAR was not exposed over AT-SPI"
    initial_status = _name(status)
    assert initial_status, "Maintenance Insights STATUS_BAR has no accessible name"

    results = _find(app, name="Maintenance Insights results")
    assert results is not None, "Selectable Maintenance Insights results were not exposed over AT-SPI"
    result_role = _role(results)
    assert result_role in {
        pyatspi.ROLE_TEXT,
        pyatspi.ROLE_LABEL,
        pyatspi.ROLE_PARAGRAPH,
    }, f"unexpected results role: {result_role!r}"

    events: list[tuple[str, str]] = []

    def listener(event) -> None:
        if _role(event.source) != pyatspi.ROLE_STATUS_BAR:
            return
        events.append((event.type, _name(event.source)))
        if events[-1][1] and events[-1][1] != initial_status:
            pyatspi.Registry.stop()

    for event_type in STATUS_EVENT_TYPES:
        pyatspi.Registry.registerEventListener(listener, event_type)

    timer = threading.Timer(8.0, pyatspi.Registry.stop)
    timer.daemon = True
    timer.start()
    try:
        _invoke(refresh)
        pyatspi.Registry.start()
    finally:
        timer.cancel()
        for event_type in STATUS_EVENT_TYPES:
            try:
                pyatspi.Registry.deregisterEventListener(listener, event_type)
            except Exception:
                pass

    assert events, "No Maintenance Insights dynamic status event crossed the live AT-SPI bus"
    assert any(name and name != initial_status for _event_type, name in events), events

    print(f"Insights AT-SPI root: {_name(app)}")
    print(f"Insights initial status: {initial_status}")
    print(f"Insights results role: {result_role}")
    print(f"Insights dynamic events observed: {len(events)}")
    for event_type, name in events[:5]:
        print(f"- {event_type}: {name}")
    print("Live Maintenance Insights AT-SPI status/results acceptance: passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
