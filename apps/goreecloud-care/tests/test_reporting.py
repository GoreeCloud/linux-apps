import json
import unittest
from datetime import datetime, timezone
from pathlib import Path

from goreecloud_care.core import Candidate, CategoryScan, DiskStats, MemoryStats
from goreecloud_care.reporting import (
    classify_disk_headroom,
    render_json_report,
    render_text_report,
    snapshot_from,
)


class ReportingTests(unittest.TestCase):
    def _snapshot(self):
        scans = {
            "cache": CategoryScan(
                key="cache",
                label="Application cache",
                candidates=[Candidate("cache", Path("/home/alice/.cache/private-name"), 4096)],
                errors=["permission denied: /home/alice/.cache/secret"],
            ),
            "trash": CategoryScan(
                key="trash",
                label="Trash",
                candidates=[Candidate("trash", Path("/home/alice/.local/share/Trash/files/private"), 2048)],
            ),
        }
        return snapshot_from(
            scans,
            DiskStats(total=1000, used=850, free=150),
            MemoryStats(total=2000, available=800, cached=300),
            generated_at=datetime(2026, 9, 6, 15, 0, tzinfo=timezone.utc),
        )

    def test_disk_headroom_bands_are_deterministic(self):
        self.assertEqual(classify_disk_headroom(DiskStats(100, 50, 50)), "comfortable")
        self.assertEqual(classify_disk_headroom(DiskStats(100, 85, 15)), "watch")
        self.assertEqual(classify_disk_headroom(DiskStats(100, 92, 8)), "low")
        self.assertEqual(classify_disk_headroom(DiskStats(100, 97, 3)), "critical")
        self.assertEqual(classify_disk_headroom(DiskStats(0, 0, 0)), "unknown")

    def test_snapshot_aggregates_without_paths_or_raw_errors(self):
        snapshot = self._snapshot()
        self.assertEqual(snapshot["maintenance"]["visible_bytes"], 6144)
        self.assertEqual(snapshot["maintenance"]["visible_items"], 2)
        self.assertEqual(snapshot["maintenance"]["scan_error_count"], 1)
        self.assertFalse(snapshot["privacy"]["contains_file_paths"])
        self.assertFalse(snapshot["privacy"]["contains_raw_scan_errors"])

        serialized = json.dumps(snapshot)
        self.assertNotIn("/home/alice", serialized)
        self.assertNotIn("private-name", serialized)
        self.assertNotIn("permission denied", serialized)

    def test_text_report_is_read_only_and_path_redacted(self):
        report = render_text_report(self._snapshot())
        self.assertIn("Read-only maintenance report", report)
        self.assertIn("Application cache", report)
        self.assertIn("This report is informational", report)
        self.assertNotIn("/home/alice", report)
        self.assertNotIn("private-name", report)

    def test_json_report_is_machine_readable(self):
        payload = json.loads(render_json_report(self._snapshot()))
        self.assertEqual(payload["schema_version"], "1")
        self.assertEqual(payload["product"], "GoreeCloud Care")
        self.assertFalse(payload["privacy"]["network_used"])
        self.assertEqual(payload["disk"]["headroom"], "watch")


if __name__ == "__main__":
    unittest.main()
