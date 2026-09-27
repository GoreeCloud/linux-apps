from __future__ import annotations

import os
import stat
import time
from dataclasses import dataclass
from pathlib import Path

from .core import CareEngine, human_bytes

LARGE_FILE_BYTES = 250 * 1024 * 1024
STALE_DOWNLOAD_DAYS = 30
STALE_DOWNLOAD_SECONDS = STALE_DOWNLOAD_DAYS * 24 * 60 * 60
MAX_RESULTS = 12
MAX_VISITED_ENTRIES = 50_000
STANDARD_USER_DIRS = ("Downloads", "Desktop", "Documents", "Pictures", "Videos", "Music")


@dataclass(frozen=True)
class FileInsight:
    display_path: str
    bytes: int
    age_days: int


@dataclass(frozen=True)
class CacheGroupInsight:
    name: str
    bytes: int
    items: int


@dataclass(frozen=True)
class InsightsSnapshot:
    cache_groups: tuple[CacheGroupInsight, ...]
    large_files: tuple[FileInsight, ...]
    stale_downloads: tuple[FileInsight, ...]
    scan_error_count: int
    visited_entries: int
    truncated: bool


def _lexical_under(path: Path, root: Path) -> bool:
    try:
        common = os.path.commonpath((os.path.abspath(path), os.path.abspath(root)))
    except ValueError:
        return False
    return common == os.path.abspath(root)


def _display_path(path: Path, home: Path) -> str:
    try:
        return "~/" + path.relative_to(home).as_posix()
    except ValueError:
        return path.name


def _age_days(mtime: float, now: float) -> int:
    return max(0, int((now - mtime) // (24 * 60 * 60)))


def _scan_user_files(
    root: Path,
    *,
    home: Path,
    uid: int,
    now: float,
    max_entries: int,
) -> tuple[list[tuple[Path, os.stat_result]], int, int, bool]:
    """Read regular user-owned files without following symlinks.

    The traversal is bounded so a Maintenance Insights request cannot become an
    unbounded home-directory crawl. It is strictly read-only.
    """
    files: list[tuple[Path, os.stat_result]] = []
    visited = 0
    errors = 0
    truncated = False
    root = root.expanduser()
    if not root.exists() or not root.is_dir():
        return files, visited, errors, truncated

    stack = [root]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    if visited >= max_entries:
                        truncated = True
                        return files, visited, errors, truncated
                    visited += 1
                    path = Path(entry.path)
                    if not _lexical_under(path, root):
                        continue
                    try:
                        info = entry.stat(follow_symlinks=False)
                    except OSError:
                        errors += 1
                        continue
                    if info.st_uid != uid:
                        continue
                    if stat.S_ISLNK(info.st_mode):
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        stack.append(path)
                        continue
                    if stat.S_ISREG(info.st_mode):
                        files.append((path, info))
        except (FileNotFoundError, PermissionError, NotADirectoryError, OSError):
            errors += 1
    return files, visited, errors, truncated


def build_insights(
    *,
    home: Path | None = None,
    uid: int | None = None,
    now: float | None = None,
    large_file_bytes: int = LARGE_FILE_BYTES,
    stale_download_days: int = STALE_DOWNLOAD_DAYS,
    max_results: int = MAX_RESULTS,
    max_visited_entries: int = MAX_VISITED_ENTRIES,
) -> InsightsSnapshot:
    """Build a local, read-only maintenance-intelligence snapshot.

    This function does not delete files, authenticate, call PolicyKit, invoke a
    privileged helper, or use the network. File paths are returned only for the
    local interactive review surface; default Care reports remain path-redacted.
    """
    resolved_home = (home or Path.home()).expanduser()
    resolved_uid = os.getuid() if uid is None else uid
    resolved_now = time.time() if now is None else now
    max_results = max(1, max_results)
    max_visited_entries = max(1, max_visited_entries)

    engine = CareEngine(home=resolved_home, uid=resolved_uid, now=resolved_now)
    cache_scan = engine.scan_category("cache")
    cache_totals: dict[str, list[int]] = {}
    for candidate in cache_scan.candidates:
        try:
            relative = candidate.path.relative_to(engine.cache_root)
            group = relative.parts[0] if relative.parts else "Other"
        except ValueError:
            group = "Other"
        values = cache_totals.setdefault(group, [0, 0])
        values[0] += candidate.size
        values[1] += 1

    cache_groups = tuple(
        CacheGroupInsight(name=name, bytes=values[0], items=values[1])
        for name, values in sorted(
            cache_totals.items(), key=lambda item: (-item[1][0], item[0].lower())
        )[:max_results]
    )

    large_files: list[FileInsight] = []
    stale_downloads: list[FileInsight] = []
    total_errors = len(cache_scan.errors)
    visited_entries = 0
    truncated = False
    stale_seconds = max(1, stale_download_days) * 24 * 60 * 60

    for dirname in STANDARD_USER_DIRS:
        remaining = max_visited_entries - visited_entries
        if remaining <= 0:
            truncated = True
            break
        root = resolved_home / dirname
        files, visited, errors, root_truncated = _scan_user_files(
            root,
            home=resolved_home,
            uid=resolved_uid,
            now=resolved_now,
            max_entries=remaining,
        )
        visited_entries += visited
        total_errors += errors
        truncated = truncated or root_truncated

        for path, info in files:
            age_days = _age_days(info.st_mtime, resolved_now)
            if info.st_size >= large_file_bytes:
                large_files.append(
                    FileInsight(
                        display_path=_display_path(path, resolved_home),
                        bytes=max(0, info.st_size),
                        age_days=age_days,
                    )
                )
            if dirname == "Downloads" and info.st_mtime <= resolved_now - stale_seconds:
                stale_downloads.append(
                    FileInsight(
                        display_path=_display_path(path, resolved_home),
                        bytes=max(0, info.st_size),
                        age_days=age_days,
                    )
                )

    large_files.sort(key=lambda item: (-item.bytes, item.display_path.lower()))
    stale_downloads.sort(key=lambda item: (-item.age_days, -item.bytes, item.display_path.lower()))

    return InsightsSnapshot(
        cache_groups=cache_groups,
        large_files=tuple(large_files[:max_results]),
        stale_downloads=tuple(stale_downloads[:max_results]),
        scan_error_count=total_errors,
        visited_entries=visited_entries,
        truncated=truncated,
    )


def render_insights_text(snapshot: InsightsSnapshot) -> str:
    lines = [
        "Maintenance Insights — read-only review",
        "Nothing in this view is selected for deletion and no maintenance runs automatically.",
        "Default Care reports remain path-redacted; paths below are shown only in this local review window.",
        "",
        "Largest stale application-cache groups (>7 days)",
    ]
    if snapshot.cache_groups:
        for item in snapshot.cache_groups:
            lines.append(f"- {item.name}: {human_bytes(item.bytes)} across {item.items} item(s)")
    else:
        lines.append("- No stale application-cache groups were found.")

    lines.extend(["", f"Large files (at least {human_bytes(LARGE_FILE_BYTES)}) in standard user folders"])
    if snapshot.large_files:
        for item in snapshot.large_files:
            lines.append(
                f"- {item.display_path}: {human_bytes(item.bytes)} • about {item.age_days} day(s) old"
            )
    else:
        lines.append("- No matching large files were found in the scanned standard user folders.")

    lines.extend(["", f"Downloads at least {STALE_DOWNLOAD_DAYS} days old"])
    if snapshot.stale_downloads:
        for item in snapshot.stale_downloads:
            lines.append(
                f"- {item.display_path}: {human_bytes(item.bytes)} • about {item.age_days} day(s) old"
            )
    else:
        lines.append("- No matching stale Downloads were found.")

    lines.extend(
        [
            "",
            f"Read-only scan details: {snapshot.visited_entries} user-folder entries inspected; "
            f"{snapshot.scan_error_count} scan error(s).",
        ]
    )
    if snapshot.truncated:
        lines.append(
            "The bounded discovery limit was reached, so this view is partial rather than exhaustive."
        )
    lines.append("Review findings manually before moving or deleting anything outside GoreeCloud Care.")
    return "\n".join(lines)
