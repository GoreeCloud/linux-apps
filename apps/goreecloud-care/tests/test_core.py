from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from goreecloud_care.core import CareEngine, STALE_SECONDS, human_bytes, parse_meminfo


class CoreTests(unittest.TestCase):
    def test_human_bytes(self):
        self.assertEqual(human_bytes(0), "0 B")
        self.assertEqual(human_bytes(1024), "1.0 KB")
        self.assertEqual(human_bytes(1024 * 1024), "1.0 MB")

    def test_meminfo_parser(self):
        stats = parse_meminfo("MemTotal: 1000 kB\nMemAvailable: 400 kB\nCached: 120 kB\nSReclaimable: 30 kB\n")
        self.assertEqual(stats.total, 1000 * 1024)
        self.assertEqual(stats.available, 400 * 1024)
        self.assertEqual(stats.cached, 150 * 1024)

    def test_cache_scan_stale_and_thumbnail_exclusion(self):
        with tempfile.TemporaryDirectory() as td:
            home = Path(td) / "home"
            cache = home / ".cache"
            thumb = cache / "thumbnails"
            cache.mkdir(parents=True)
            thumb.mkdir()
            old = cache / "old.bin"
            new = cache / "new.bin"
            tn = thumb / "thumb.png"
            old.write_bytes(b"old")
            new.write_bytes(b"new")
            tn.write_bytes(b"thumb")
            now = time.time()
            old_time = now - STALE_SECONDS - 10
            os.utime(old, (old_time, old_time))
            engine = CareEngine(home=home, temp_root=Path(td) / "tmp", uid=os.getuid(), now=now)
            cache_scan = engine.scan_category("cache")
            thumb_scan = engine.scan_category("thumbnails")
            self.assertEqual([x.path.name for x in cache_scan.candidates], ["old.bin"])
            self.assertEqual([x.path.name for x in thumb_scan.candidates], ["thumb.png"])

    def test_symlink_is_not_followed(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            home = base / "home"
            cache = home / ".cache"
            outside = base / "outside.txt"
            cache.mkdir(parents=True)
            outside.write_text("keep", encoding="utf-8")
            link = cache / "link"
            link.symlink_to(outside)
            now = time.time()
            old_time = now - STALE_SECONDS - 10
            os.utime(link, (old_time, old_time), follow_symlinks=False)
            engine = CareEngine(home=home, temp_root=base / "tmp", uid=os.getuid(), now=now)
            scan = engine.scan_category("cache")
            self.assertEqual(len(scan.candidates), 1)
            engine.cleanup(scan)
            self.assertTrue(outside.exists())
            self.assertFalse(link.exists())

    def test_cleanup_never_deletes_fresh_cache(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            home = base / "home"
            cache = home / ".cache"
            cache.mkdir(parents=True)
            stale = cache / "stale"
            fresh = cache / "fresh"
            stale.write_bytes(b"12345")
            fresh.write_bytes(b"67890")
            now = time.time()
            old_time = now - STALE_SECONDS - 10
            os.utime(stale, (old_time, old_time))
            engine = CareEngine(home=home, temp_root=base / "tmp", uid=os.getuid(), now=now)
            scan = engine.scan_category("cache")
            result = engine.cleanup(scan)
            self.assertEqual(result.deleted_count, 1)
            self.assertFalse(stale.exists())
            self.assertTrue(fresh.exists())

    def test_empty_trash_removes_files_and_info_but_not_symlink_target(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            home = base / "home"
            files = home / ".local/share/Trash/files"
            info = home / ".local/share/Trash/info"
            files.mkdir(parents=True)
            info.mkdir(parents=True)
            target = base / "outside.txt"
            target.write_text("outside", encoding="utf-8")
            (files / "plain.txt").write_text("trash", encoding="utf-8")
            (files / "linked").symlink_to(target)
            (info / "plain.txt.trashinfo").write_text("[Trash Info]", encoding="utf-8")
            engine = CareEngine(home=home, temp_root=base / "tmp", uid=os.getuid())
            result = engine.empty_trash()
            self.assertFalse(any(files.iterdir()))
            self.assertFalse(any(info.iterdir()))
            self.assertTrue(target.exists())
            self.assertGreaterEqual(result.deleted_count, 3)

    def test_temp_scan_only_owned_stale_files(self):
        with tempfile.TemporaryDirectory() as td:
            base = Path(td)
            home = base / "home"
            tmp = base / "tmp"
            tmp.mkdir()
            stale = tmp / "stale.tmp"
            fresh = tmp / "fresh.tmp"
            stale.write_text("stale", encoding="utf-8")
            fresh.write_text("fresh", encoding="utf-8")
            now = time.time()
            old_time = now - STALE_SECONDS - 10
            os.utime(stale, (old_time, old_time))
            engine = CareEngine(home=home, temp_root=tmp, uid=os.getuid(), now=now)
            scan = engine.scan_category("temp")
            self.assertEqual([x.path.name for x in scan.candidates], ["stale.tmp"])


if __name__ == "__main__":
    unittest.main()
