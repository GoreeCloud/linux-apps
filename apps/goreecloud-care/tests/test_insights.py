from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from goreecloud_care.insights import build_insights, render_insights_text


class InsightsTests(unittest.TestCase):
    def _write(self, path: Path, size: int, *, mtime: float) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as handle:
            handle.truncate(size)
        os.utime(path, (mtime, mtime))

    def test_cache_breakdown_groups_only_stale_application_cache(self):
        now = time.time()
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            self._write(home / ".cache" / "alpha" / "old.bin", 4096, mtime=now - 10 * 86400)
            self._write(home / ".cache" / "alpha" / "fresh.bin", 8192, mtime=now - 86400)
            self._write(home / ".cache" / "beta" / "old.bin", 2048, mtime=now - 20 * 86400)
            self._write(home / ".cache" / "thumbnails" / "thumb.png", 65536, mtime=now - 20 * 86400)

            snapshot = build_insights(home=home, uid=os.getuid(), now=now)
            groups = {group.name: group for group in snapshot.cache_groups}

            self.assertEqual(groups["alpha"].bytes, 4096)
            self.assertEqual(groups["alpha"].items, 1)
            self.assertEqual(groups["beta"].bytes, 2048)
            self.assertNotIn("thumbnails", groups)

    def test_large_file_discovery_is_bounded_to_standard_user_folders_and_no_symlink_follow(self):
        now = time.time()
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            self._write(home / "Downloads" / "large.iso", 4096, mtime=now - 40 * 86400)
            self._write(home / "private.bin", 8192, mtime=now - 40 * 86400)
            outside = home / "outside.bin"
            self._write(outside, 16384, mtime=now - 40 * 86400)
            (home / "Downloads" / "linked.bin").symlink_to(outside)

            snapshot = build_insights(
                home=home,
                uid=os.getuid(),
                now=now,
                large_file_bytes=1024,
            )
            paths = {item.display_path for item in snapshot.large_files}

            self.assertIn("~/Downloads/large.iso", paths)
            self.assertNotIn("~/private.bin", paths)
            self.assertNotIn("~/Downloads/linked.bin", paths)

    def test_stale_downloads_require_age_threshold(self):
        now = time.time()
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            self._write(home / "Downloads" / "old.zip", 2048, mtime=now - 45 * 86400)
            self._write(home / "Downloads" / "recent.zip", 2048, mtime=now - 5 * 86400)

            snapshot = build_insights(home=home, uid=os.getuid(), now=now)
            paths = {item.display_path for item in snapshot.stale_downloads}

            self.assertIn("~/Downloads/old.zip", paths)
            self.assertNotIn("~/Downloads/recent.zip", paths)

    def test_discovery_limit_reports_partial_snapshot(self):
        now = time.time()
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            for index in range(5):
                self._write(
                    home / "Downloads" / f"file-{index}.bin",
                    1024,
                    mtime=now - 45 * 86400,
                )

            snapshot = build_insights(
                home=home,
                uid=os.getuid(),
                now=now,
                large_file_bytes=1,
                max_visited_entries=2,
            )

            self.assertTrue(snapshot.truncated)
            self.assertEqual(snapshot.visited_entries, 2)

    def test_rendered_insights_are_explicitly_review_only_and_home_relative(self):
        now = time.time()
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            self._write(home / "Downloads" / "old-large.bin", 4096, mtime=now - 45 * 86400)

            snapshot = build_insights(
                home=home,
                uid=os.getuid(),
                now=now,
                large_file_bytes=1024,
            )
            text = render_insights_text(snapshot)

            self.assertIn("read-only review", text)
            self.assertIn("Nothing in this view is selected for deletion", text)
            self.assertIn("~/Downloads/old-large.bin", text)
            self.assertNotIn(str(home), text)


if __name__ == "__main__":
    unittest.main()
