from __future__ import annotations

import os
import shutil
import stat
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator

STALE_DAYS = 7
STALE_SECONDS = STALE_DAYS * 24 * 60 * 60


@dataclass(frozen=True)
class Candidate:
    category: str
    path: Path
    size: int


@dataclass
class CategoryScan:
    key: str
    label: str
    candidates: list[Candidate] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def bytes(self) -> int:
        return sum(item.size for item in self.candidates)

    @property
    def count(self) -> int:
        return len(self.candidates)


@dataclass
class CleanupResult:
    deleted_count: int = 0
    reclaimed_bytes: int = 0
    errors: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class MemoryStats:
    total: int
    available: int
    cached: int

    @property
    def used_estimate(self) -> int:
        return max(0, self.total - self.available)


@dataclass(frozen=True)
class DiskStats:
    total: int
    used: int
    free: int


def human_bytes(value: int) -> str:
    size = float(max(0, value))
    units = ("B", "KB", "MB", "GB", "TB", "PB")
    for unit in units:
        if size < 1024.0 or unit == units[-1]:
            return f"{size:.0f} {unit}" if unit == "B" else f"{size:.1f} {unit}"
        size /= 1024.0
    return f"{size:.1f} PB"


def parse_meminfo(text: str) -> MemoryStats:
    values: dict[str, int] = {}
    for line in text.splitlines():
        if ":" not in line:
            continue
        key, raw = line.split(":", 1)
        parts = raw.strip().split()
        if not parts:
            continue
        try:
            value = int(parts[0])
        except ValueError:
            continue
        multiplier = 1024 if len(parts) > 1 and parts[1].lower() == "kb" else 1
        values[key] = value * multiplier

    total = values.get("MemTotal", 0)
    available = values.get("MemAvailable", values.get("MemFree", 0))
    cached = values.get("Cached", 0) + values.get("SReclaimable", 0)
    return MemoryStats(total=total, available=available, cached=cached)


def read_memory_stats(meminfo: Path = Path("/proc/meminfo")) -> MemoryStats:
    try:
        return parse_meminfo(meminfo.read_text(encoding="utf-8"))
    except OSError:
        return MemoryStats(total=0, available=0, cached=0)


def read_disk_stats(path: Path = Path("/")) -> DiskStats:
    usage = shutil.disk_usage(path)
    return DiskStats(total=usage.total, used=usage.used, free=usage.free)


def _lexical_under(path: Path, root: Path) -> bool:
    try:
        common = os.path.commonpath((os.path.abspath(path), os.path.abspath(root)))
    except ValueError:
        return False
    return common == os.path.abspath(root)


def _entry_size(entry: os.DirEntry[str]) -> int:
    try:
        info = entry.stat(follow_symlinks=False)
    except OSError:
        return 0
    return max(0, info.st_size)


def _iter_files(
    root: Path,
    *,
    category: str,
    older_than: float | None,
    uid: int | None = None,
    excluded_roots: Iterable[Path] = (),
) -> Iterator[Candidate]:
    """Yield individual files/symlinks without following symlinks.

    Directories are traversed only if they remain lexically within the trusted root.
    Deletion operates on the yielded leaf nodes and only prunes directories after they
    become empty, avoiding broad recursive deletion of fresh or foreign content.
    """
    root = root.expanduser()
    if not root.exists() or not root.is_dir():
        return

    excluded = tuple(os.path.abspath(p.expanduser()) for p in excluded_roots)
    stack = [root]
    while stack:
        current = stack.pop()
        try:
            with os.scandir(current) as entries:
                for entry in entries:
                    p = Path(entry.path)
                    absolute = os.path.abspath(p)
                    if any(absolute == ex or absolute.startswith(ex + os.sep) for ex in excluded):
                        continue
                    if not _lexical_under(p, root):
                        continue
                    try:
                        info = entry.stat(follow_symlinks=False)
                    except OSError:
                        continue
                    if uid is not None and info.st_uid != uid:
                        continue
                    if entry.is_symlink():
                        if older_than is None or info.st_mtime <= older_than:
                            yield Candidate(category, p, max(0, info.st_size))
                        continue
                    if stat.S_ISDIR(info.st_mode):
                        stack.append(p)
                        continue
                    if stat.S_ISREG(info.st_mode):
                        if older_than is None or info.st_mtime <= older_than:
                            yield Candidate(category, p, max(0, info.st_size))
        except (FileNotFoundError, PermissionError, NotADirectoryError):
            continue


def _prune_empty_dirs(root: Path, *, uid: int | None = None) -> None:
    if not root.exists() or not root.is_dir():
        return
    for current, dirs, _files in os.walk(root, topdown=False, followlinks=False):
        for dirname in dirs:
            p = Path(current) / dirname
            if not _lexical_under(p, root):
                continue
            try:
                info = p.lstat()
                if stat.S_ISLNK(info.st_mode):
                    continue
                if uid is not None and info.st_uid != uid:
                    continue
                p.rmdir()
            except OSError:
                pass


class CareEngine:
    CATEGORY_LABELS = {
        "cache": "Application cache",
        "thumbnails": "Thumbnail cache",
        "temp": "Temporary files",
        "trash": "Trash",
        "apt": "APT package cache",
    }

    def __init__(
        self,
        home: Path | None = None,
        temp_root: Path = Path("/tmp"),
        apt_root: Path = Path("/var/cache/apt/archives"),
        uid: int | None = None,
        now: float | None = None,
    ) -> None:
        self.home = (home or Path.home()).expanduser()
        self.cache_root = self.home / ".cache"
        self.thumbnail_root = self.cache_root / "thumbnails"
        self.trash_root = self.home / ".local" / "share" / "Trash"
        self.trash_files = self.trash_root / "files"
        self.trash_info = self.trash_root / "info"
        self.temp_root = temp_root
        self.apt_root = apt_root
        self.uid = os.getuid() if uid is None else uid
        self.now = time.time() if now is None else now

    @property
    def stale_before(self) -> float:
        return self.now - STALE_SECONDS

    def scan_category(self, key: str) -> CategoryScan:
        if key not in self.CATEGORY_LABELS:
            raise ValueError(f"Unknown category: {key}")
        result = CategoryScan(key=key, label=self.CATEGORY_LABELS[key])
        try:
            if key == "cache":
                result.candidates.extend(
                    _iter_files(
                        self.cache_root,
                        category=key,
                        older_than=self.stale_before,
                        uid=self.uid,
                        excluded_roots=(self.thumbnail_root,),
                    )
                )
            elif key == "thumbnails":
                result.candidates.extend(
                    _iter_files(
                        self.thumbnail_root,
                        category=key,
                        older_than=None,
                        uid=self.uid,
                    )
                )
            elif key == "temp":
                result.candidates.extend(
                    _iter_files(
                        self.temp_root,
                        category=key,
                        older_than=self.stale_before,
                        uid=self.uid,
                    )
                )
            elif key == "trash":
                result.candidates.extend(
                    _iter_files(
                        self.trash_files,
                        category=key,
                        older_than=None,
                        uid=self.uid,
                    )
                )
            elif key == "apt":
                if self.apt_root.exists():
                    for p in self.apt_root.glob("*.deb"):
                        try:
                            info = p.lstat()
                            if stat.S_ISREG(info.st_mode):
                                result.candidates.append(Candidate(key, p, max(0, info.st_size)))
                        except OSError:
                            continue
        except OSError as exc:
            result.errors.append(str(exc))
        return result

    def scan_all(self) -> dict[str, CategoryScan]:
        return {key: self.scan_category(key) for key in self.CATEGORY_LABELS}

    def cleanup(self, scan: CategoryScan) -> CleanupResult:
        if scan.key not in {"cache", "thumbnails", "temp"}:
            raise ValueError("Generic cleanup is limited to non-privileged cache/temp categories")
        trusted_root = {
            "cache": self.cache_root,
            "thumbnails": self.thumbnail_root,
            "temp": self.temp_root,
        }[scan.key]
        result = CleanupResult()
        for item in scan.candidates:
            if item.category != scan.key or not _lexical_under(item.path, trusted_root):
                result.errors.append("Rejected a cleanup candidate outside its trusted root")
                continue
            try:
                info = item.path.lstat()
                if self.uid is not None and info.st_uid != self.uid:
                    result.errors.append("Skipped an item no longer owned by the active user")
                    continue
                if stat.S_ISDIR(info.st_mode) and not stat.S_ISLNK(info.st_mode):
                    result.errors.append("Skipped an unexpected directory cleanup candidate")
                    continue
                item.path.unlink()
                result.deleted_count += 1
                result.reclaimed_bytes += item.size
            except FileNotFoundError:
                continue
            except OSError as exc:
                result.errors.append(str(exc))
        _prune_empty_dirs(trusted_root, uid=self.uid)
        return result

    def empty_trash(self) -> CleanupResult:
        """Permanently remove Trash contents. Caller must obtain explicit confirmation."""
        result = CleanupResult()
        for root in (self.trash_files, self.trash_info):
            if not root.exists() or not root.is_dir():
                continue
            try:
                children = list(os.scandir(root))
            except OSError as exc:
                result.errors.append(str(exc))
                continue
            for entry in children:
                p = Path(entry.path)
                if not _lexical_under(p, root):
                    result.errors.append("Rejected a Trash entry outside its trusted root")
                    continue
                try:
                    info = entry.stat(follow_symlinks=False)
                    if info.st_uid != self.uid:
                        result.errors.append("Skipped a Trash entry not owned by the active user")
                        continue
                    if stat.S_ISDIR(info.st_mode) and not self._tree_all_owned_no_follow(p):
                        result.errors.append("Skipped a Trash tree containing an entry not owned by the active user")
                        continue
                    size = self._tree_size_no_follow(p) if stat.S_ISDIR(info.st_mode) else max(0, info.st_size)
                    self._remove_no_follow(p, root)
                    result.deleted_count += 1
                    if root == self.trash_files:
                        result.reclaimed_bytes += size
                except FileNotFoundError:
                    continue
                except OSError as exc:
                    result.errors.append(str(exc))
        return result

    def _tree_all_owned_no_follow(self, root: Path) -> bool:
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                info = current.lstat()
            except OSError:
                return False
            if info.st_uid != self.uid:
                return False
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                continue
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        stack.append(Path(entry.path))
            except OSError:
                return False
        return True

    def _tree_size_no_follow(self, root: Path) -> int:
        total = 0
        stack = [root]
        while stack:
            current = stack.pop()
            try:
                info = current.lstat()
            except OSError:
                continue
            if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
                total += max(0, info.st_size)
                continue
            try:
                with os.scandir(current) as entries:
                    for entry in entries:
                        stack.append(Path(entry.path))
            except OSError:
                continue
        return total

    def _remove_no_follow(self, path: Path, trusted_root: Path) -> None:
        if not _lexical_under(path, trusted_root):
            raise ValueError("Refusing to remove outside trusted root")
        info = path.lstat()
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            path.unlink()
            return
        with os.scandir(path) as entries:
            for entry in list(entries):
                child = Path(entry.path)
                child_info = entry.stat(follow_symlinks=False)
                if child_info.st_uid != self.uid:
                    raise PermissionError("Trash tree contains an entry not owned by the active user")
                self._remove_no_follow(child, trusted_root)
        path.rmdir()
