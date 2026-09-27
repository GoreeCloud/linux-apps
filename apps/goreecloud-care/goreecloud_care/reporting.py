from __future__ import annotations

import json
from datetime import datetime, timezone
from typing import Mapping

from .core import (
    CareEngine,
    CategoryScan,
    DiskStats,
    MemoryStats,
    human_bytes,
    read_disk_stats,
    read_memory_stats,
)

REPORT_SCHEMA_VERSION = "1"
ROUTINE_KEYS = {"cache", "thumbnails", "temp"}


def classify_disk_headroom(disk: DiskStats) -> str:
    """Return a conservative, descriptive disk-headroom band.

    This is an informational signal only. It never initiates cleanup and does
    not claim filesystem health or predict failure.
    """
    if disk.total <= 0:
        return "unknown"
    free_ratio = max(0.0, min(1.0, disk.free / disk.total))
    if free_ratio < 0.05:
        return "critical"
    if free_ratio < 0.10:
        return "low"
    if free_ratio < 0.20:
        return "watch"
    return "comfortable"


def snapshot_from(
    scans: Mapping[str, CategoryScan],
    disk: DiskStats,
    memory: MemoryStats,
    *,
    generated_at: datetime | None = None,
) -> dict:
    """Build a path-redacted, read-only maintenance snapshot.

    Candidate file paths and raw scan-error strings are intentionally omitted so
    the report can be copied into support or automation workflows without
    exposing local filenames or directory structure by default.
    """
    when = generated_at or datetime.now(timezone.utc)
    if when.tzinfo is None:
        when = when.replace(tzinfo=timezone.utc)

    categories: list[dict] = []
    visible_bytes = 0
    visible_items = 0
    scan_error_count = 0

    for key, scan in scans.items():
        category_error_count = len(scan.errors)
        scan_error_count += category_error_count
        visible_bytes += scan.bytes
        visible_items += scan.count
        categories.append(
            {
                "key": key,
                "label": scan.label,
                "bytes": scan.bytes,
                "items": scan.count,
                "scan_error_count": category_error_count,
                "routine_cleanup_selectable": key in ROUTINE_KEYS,
            }
        )

    free_percent = (disk.free / disk.total * 100.0) if disk.total > 0 else None
    available_percent = (
        memory.available / memory.total * 100.0 if memory.total > 0 else None
    )

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "product": "GoreeCloud Care",
        "mode": "read-only-local-maintenance-report",
        "generated_at": when.astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
        "privacy": {
            "network_used": False,
            "telemetry_used": False,
            "contains_file_paths": False,
            "contains_raw_scan_errors": False,
        },
        "disk": {
            "total_bytes": disk.total,
            "used_bytes": disk.used,
            "free_bytes": disk.free,
            "free_percent": free_percent,
            "headroom": classify_disk_headroom(disk),
        },
        "memory": {
            "total_bytes": memory.total,
            "available_bytes": memory.available,
            "available_percent": available_percent,
            "file_cache_bytes": memory.cached,
        },
        "maintenance": {
            "visible_bytes": visible_bytes,
            "visible_items": visible_items,
            "scan_error_count": scan_error_count,
            "categories": categories,
        },
    }


def build_snapshot(engine: CareEngine | None = None) -> dict:
    active_engine = engine or CareEngine()
    return snapshot_from(
        active_engine.scan_all(),
        read_disk_stats(),
        read_memory_stats(),
    )


def _percent(value: float | None) -> str:
    return "unknown" if value is None else f"{value:.1f}%"


def render_text_report(snapshot: Mapping) -> str:
    disk = snapshot["disk"]
    memory = snapshot["memory"]
    maintenance = snapshot["maintenance"]

    lines = [
        "GoreeCloud Care — Read-only maintenance report",
        f"Generated: {snapshot['generated_at']}",
        "Privacy: local-only; no telemetry; file paths and raw scan errors omitted",
        "",
        "System",
        (
            f"- Disk: {human_bytes(disk['free_bytes'])} free of "
            f"{human_bytes(disk['total_bytes'])} "
            f"({_percent(disk['free_percent'])} free; headroom: {disk['headroom']})"
        ),
        (
            f"- Memory: {human_bytes(memory['available_bytes'])} available of "
            f"{human_bytes(memory['total_bytes'])} "
            f"({_percent(memory['available_percent'])} available)"
        ),
        f"- File cache: about {human_bytes(memory['file_cache_bytes'])}",
        "",
        "Maintenance preview",
        (
            f"- Visible total: {human_bytes(maintenance['visible_bytes'])} across "
            f"{maintenance['visible_items']} item(s)"
        ),
        f"- Scan errors: {maintenance['scan_error_count']}",
    ]

    for category in maintenance["categories"]:
        selectable = "routine-selectable" if category["routine_cleanup_selectable"] else "separate action"
        lines.append(
            f"- {category['label']}: {human_bytes(category['bytes'])}, "
            f"{category['items']} item(s), {selectable}, "
            f"scan errors: {category['scan_error_count']}"
        )

    lines.extend(
        [
            "",
            "This report is informational. It does not delete files, authenticate, or perform maintenance.",
        ]
    )
    return "\n".join(lines)


def render_json_report(snapshot: Mapping) -> str:
    return json.dumps(snapshot, indent=2, sort_keys=True)
