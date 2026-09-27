from __future__ import annotations

import sys

from gi.repository import GLib

from . import __version__

# Keep both GLib identities explicit before Gtk.Application startup. AT-SPI on
# the representative Zorin OS desktop derives the application-root name from
# the GLib program name, while user-facing GTK surfaces use the application
# name. Setting both prevents Python's module basename (__main__.py) from
# leaking into assistive-technology discovery.
GLib.set_prgname("GoreeCloud Care")
GLib.set_application_name("GoreeCloud Care")


def _install_native_ui_contract() -> None:
    """Install shared focus and latest Glaze UI Development providers for GTK modes."""
    from .focus_resilience import install_focus_resilience_provider
    from .glaze_v13_global import install_glaze_v13_global_style

    # The focus-only fallback remains one priority below ordinary application
    # styling. The Proposed V1.3 process-level provider is removed automatically
    # when HighContrast is effective, preserving system palette authority.
    install_focus_resilience_provider()
    install_glaze_v13_global_style()


def _run() -> int:
    args = sys.argv[1:]
    report_requested = "--report" in args
    json_report_requested = "--report-json" in args
    insights_ui_requested = "--insights-ui" in args
    api_version_requested = "--api-version" in args
    health_json_requested = "--health-json" in args
    privacy_status_requested = "--privacy-status-json" in args
    security_status_requested = "--security-status-json" in args
    continuity_status_requested = "--continuity-status-json" in args

    exclusive_modes = [
        report_requested,
        json_report_requested,
        insights_ui_requested,
        api_version_requested,
        health_json_requested,
        privacy_status_requested,
        security_status_requested,
        continuity_status_requested,
        "--version" in args,
    ]
    if sum(bool(mode) for mode in exclusive_modes) > 1:
        print("goreecloud-care: choose exactly one command mode", file=sys.stderr)
        return 2

    if "--version" in args:
        unexpected = [arg for arg in args if arg != "--version"]
        if unexpected:
            print("goreecloud-care: --version does not accept additional arguments", file=sys.stderr)
            return 2
        print(__version__)
        return 0

    if api_version_requested:
        unexpected = [arg for arg in args if arg != "--api-version"]
        if unexpected:
            print("goreecloud-care: --api-version does not accept additional arguments", file=sys.stderr)
            return 2
        from .platform_status import API_VERSION

        print(API_VERSION)
        return 0

    if health_json_requested or privacy_status_requested or security_status_requested or continuity_status_requested:
        known = {
            "--health-json",
            "--privacy-status-json",
            "--security-status-json",
            "--continuity-status-json",
        }
        unexpected = [arg for arg in args if arg not in known]
        if unexpected:
            print(
                "goreecloud-care: local status mode does not accept additional arguments: "
                + " ".join(unexpected),
                file=sys.stderr,
            )
            return 2
        from .platform_status import (
            build_continuity_status,
            build_health_status,
            build_privacy_status,
            build_wardveil_status,
            render_json,
        )

        if health_json_requested:
            payload = build_health_status()
        elif privacy_status_requested:
            payload = build_privacy_status()
        elif security_status_requested:
            payload = build_wardveil_status()
        else:
            payload = build_continuity_status()
        print(render_json(payload))
        return 0

    if insights_ui_requested:
        unexpected = [arg for arg in args if arg != "--insights-ui"]
        if unexpected:
            print(
                "goreecloud-care: --insights-ui does not accept additional arguments: "
                + " ".join(unexpected),
                file=sys.stderr,
            )
            return 2

        from .insights_window import main as insights_main

        _install_native_ui_contract()
        return insights_main()

    if report_requested or json_report_requested:
        unexpected = [arg for arg in args if arg not in {"--report", "--report-json"}]
        if unexpected:
            print(
                "goreecloud-care: report mode does not accept additional arguments: "
                + " ".join(unexpected),
                file=sys.stderr,
            )
            return 2

        from .reporting import build_snapshot, render_json_report, render_text_report

        snapshot = build_snapshot()
        print(render_json_report(snapshot) if json_report_requested else render_text_report(snapshot))
        return 0

    if args:
        print("goreecloud-care: unrecognized argument(s): " + " ".join(args), file=sys.stderr)
        return 2

    from .app import main

    _install_native_ui_contract()
    return main()


raise SystemExit(_run())
