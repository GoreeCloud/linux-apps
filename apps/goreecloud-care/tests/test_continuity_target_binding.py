from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import tempfile
import unittest

from goreecloud_care.platform_status import build_continuity_status


NOW = datetime(2026, 9, 7, 19, 10, tzinfo=timezone.utc)
REVISION = "1" * 40
TREE = "2" * 40
PACKAGE_SHA = "3" * 64


class ContinuityTargetBindingTests(unittest.TestCase):
    def _write(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.parent.chmod(0o755)
        path.write_text(json.dumps(payload) + "\n", encoding="utf-8")
        path.chmod(0o644)

    def _provenance(self) -> dict:
        return {
            "schema_version": 1,
            "application": "GoreeCloud Care",
            "producer": "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care",
            "source_revision": REVISION,
            "source_tree": TREE,
            "runtime_version": "0.1.0",
            "package_version": "0.1.0",
            "source_date_epoch": 1_788_800_000,
            "package_sha256_embedded": False,
        }

    def _acceptance(self, target_name: str, *, promoted: bool) -> dict:
        return {
            "schema_version": 1,
            "application": "GoreeCloud Care",
            "producer": "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care",
            "candidate": {
                "source_revision": REVISION,
                "source_tree": TREE,
                "runtime_version": "0.1.0",
                "package_version": "0.1.0",
                "package_sha256": PACKAGE_SHA,
            },
            "target": {
                "name": target_name,
                "representative": True,
                "status": "passed",
            },
            "dimensions": ["restore_capability", "provenance"],
            "evidence": {
                "local_tests": 143,
                "source_validation": "passed",
                "package_lifecycle": "passed",
                "references": ["fixture"],
            },
            "acceptance": {
                "target_runtime_status": "passed",
                "exact_revision_accepted": True,
                "everkeep_integration_promoted": promoted,
                "everkeep_ready_promoted": promoted,
                "freshness_rule": "Exact 0.1.0 candidate and representative target only.",
            },
        }

    def test_wrong_os_cannot_satisfy_representative_target_acceptance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            provenance = root / "package" / "build-provenance.json"
            representative = root / "representative" / "target.json"
            everkeep = root / "everkeep" / "target.json"
            self._write(provenance, self._provenance())
            self._write(
                representative,
                self._acceptance("Ubuntu 24.04 representative runner", promoted=False),
            )
            self._write(
                everkeep,
                self._acceptance("Ubuntu 24.04 representative runner", promoted=True),
            )

            payload = build_continuity_status(
                NOW,
                provenance_path=provenance,
                representative_acceptance_path=representative,
                everkeep_acceptance_path=everkeep,
                expected_uid=os.geteuid(),
            )
            self.assertEqual(payload["state"], "attention")
            self.assertEqual(payload["stage"], "target-acceptance-required")

    def test_zorin_17_3_target_can_satisfy_exact_promoted_chain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            provenance = root / "package" / "build-provenance.json"
            representative = root / "representative" / "target.json"
            everkeep = root / "everkeep" / "target.json"
            self._write(provenance, self._provenance())
            self._write(
                representative,
                self._acceptance("Zorin OS 17.3 representative laptop", promoted=False),
            )
            self._write(
                everkeep,
                self._acceptance("Zorin OS 17.3 representative laptop", promoted=True),
            )

            payload = build_continuity_status(
                NOW,
                provenance_path=provenance,
                representative_acceptance_path=representative,
                everkeep_acceptance_path=everkeep,
                expected_uid=os.geteuid(),
            )
            self.assertEqual(payload["state"], "ready")
            self.assertEqual(payload["stage"], "everkeep-promoted")
            self.assertEqual(payload["freshness"], "exact-build-bound")


if __name__ == "__main__":
    unittest.main()
