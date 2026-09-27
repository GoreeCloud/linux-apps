import json
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
import stat
import tempfile
import unittest

from goreecloud_care.platform_status import (
    API_VERSION,
    build_continuity_status,
    build_health_status,
    build_privacy_status,
    build_wardveil_status,
    evaluate_privileged_boundary,
    render_json,
)


NOW = datetime(2026, 9, 6, 18, 30, tzinfo=timezone.utc)
SOURCE_REVISION = "a" * 40
SOURCE_TREE = "b" * 40
PACKAGE_SHA256 = "c" * 64


class PlatformStatusTests(unittest.TestCase):
    def test_health_status_is_minimized_local_and_read_only(self):
        payload = build_health_status(NOW)
        self.assertEqual(payload["schema_version"], API_VERSION)
        self.assertEqual(payload["product"], "GoreeCloud Care")
        self.assertEqual(payload["state"], "ready")
        self.assertTrue(payload["local_only"])
        self.assertFalse(payload["network_used"])
        self.assertFalse(payload["telemetry_used"])
        self.assertFalse(payload["privileged_action_performed"])

    def test_privacy_status_fails_closed_to_pending_acceptance(self):
        payload = build_privacy_status(NOW)
        self.assertEqual(payload["state"], "development")
        self.assertFalse(payload["acceptance"]["production_approved"])
        self.assertTrue(payload["acceptance"]["runtime_acceptance_required"])
        self.assertNotIn("valid_until", payload)
        self.assertTrue(all(item["state"] == "pending-acceptance" for item in payload["capabilities"]))
        self.assertFalse(payload["privacy"]["raw_private_activity_included"])
        self.assertFalse(payload["privacy"]["contains_credentials"])
        self.assertFalse(payload["privacy"]["contains_identifiers"])

    def test_privacy_status_can_represent_explicit_future_acceptance(self):
        payload = build_privacy_status(NOW, production_approved=True)
        self.assertEqual(payload["state"], "protected")
        self.assertTrue(payload["acceptance"]["production_approved"])
        self.assertIn("valid_until", payload)
        self.assertTrue(all(item["state"] == "active" for item in payload["capabilities"]))

    def _make_file(self, path: Path, mode: int) -> None:
        path.write_text("fixture\n", encoding="utf-8")
        path.chmod(mode)

    def test_privileged_boundary_passes_only_with_secure_fixed_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            helper = root / "helper"
            policy = root / "policy"
            pkexec = root / "pkexec"
            self._make_file(helper, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            self._make_file(policy, stat.S_IRUSR | stat.S_IWUSR)
            self._make_file(pkexec, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            checks = evaluate_privileged_boundary(
                helper,
                policy,
                pkexec,
                expected_uid=os.geteuid(),
            )
            self.assertTrue(all(checks.values()))

            payload = build_wardveil_status(
                NOW,
                helper_path=helper,
                policy_path=policy,
                pkexec_path=pkexec,
                expected_uid=os.geteuid(),
            )
            self.assertEqual(payload["state"], "protected")
            self.assertEqual(payload["source_state"], "passing")
            self.assertEqual(payload["evidence"]["status"], "current")
            self.assertEqual(
                payload["evidence"]["reference"],
                "local-cli://goreecloud-care/security-status",
            )
            self.assertEqual(payload["scope"]["id"], "goreecloud-care")
            self.assertEqual(
                payload["authority"]["control"],
                "local-maintenance-privilege-boundary",
            )
            self.assertTrue(payload["authority"]["authoritative"])
            self.assertFalse(payload["claim"]["protected_by_wardveil"])
            self.assertEqual(
                payload["evidence"]["valid_until"],
                (NOW + timedelta(minutes=15)).isoformat().replace("+00:00", "Z"),
            )

    def test_wardveil_status_is_minimized_textual_and_not_a_protection_claim(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            helper = root / "helper"
            policy = root / "policy"
            pkexec = root / "pkexec"
            self._make_file(helper, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            self._make_file(policy, stat.S_IRUSR | stat.S_IWUSR)
            self._make_file(pkexec, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            payload = build_wardveil_status(
                NOW,
                helper_path=helper,
                policy_path=policy,
                pkexec_path=pkexec,
                expected_uid=os.geteuid(),
            )

            self.assertIsInstance(payload["state"], str)
            self.assertIsInstance(payload["source_state"], str)
            self.assertTrue(payload["evidence"]["summary"])
            self.assertTrue(payload["privacy"]["details_withheld"])
            self.assertTrue(payload["privacy"]["redactions"])
            self.assertFalse(payload["claim"]["protected_by_wardveil"])

            serialized = json.dumps(payload, sort_keys=True).lower()
            for forbidden in (
                "password",
                "authentication token",
                "private key",
                "recovery code",
                "/home/",
                "username",
                "user_email",
            ):
                self.assertNotIn(forbidden, serialized)

    def test_privileged_boundary_fails_closed_on_writable_or_missing_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            helper = root / "helper"
            policy = root / "policy"
            pkexec = root / "pkexec"
            self._make_file(helper, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR | stat.S_IWGRP)
            self._make_file(policy, stat.S_IRUSR | stat.S_IWUSR)
            self._make_file(pkexec, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)
            payload = build_wardveil_status(
                NOW,
                helper_path=helper,
                policy_path=policy,
                pkexec_path=pkexec,
                expected_uid=os.geteuid(),
            )
            self.assertEqual(payload["state"], "attention")
            self.assertEqual(payload["source_state"], "non-passing")
            self.assertFalse(payload["claim"]["protected_by_wardveil"])
            self.assertNotIn("valid_until", payload["evidence"])

            helper.unlink()
            checks = evaluate_privileged_boundary(
                helper,
                policy,
                pkexec,
                expected_uid=os.geteuid(),
            )
            self.assertFalse(checks["helper_root_owned_nonwritable"])

    def _write_secure_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.parent.chmod(0o755)
        path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        path.chmod(0o644)

    def _build_provenance(self) -> dict:
        return {
            "schema_version": 1,
            "application": "GoreeCloud Care",
            "producer": "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care",
            "source_revision": SOURCE_REVISION,
            "source_tree": SOURCE_TREE,
            "runtime_version": "0.1.0",
            "package_version": "0.1.0",
            "source_date_epoch": 1_788_800_000,
            "package_sha256_embedded": False,
        }

    def _acceptance_record(
        self,
        *,
        package_sha256: str = PACKAGE_SHA256,
        source_revision: str = SOURCE_REVISION,
        promoted: bool = False,
    ) -> dict:
        return {
            "schema_version": 1,
            "application": "GoreeCloud Care",
            "producer": "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care",
            "candidate": {
                "source_revision": source_revision,
                "source_tree": SOURCE_TREE,
                "runtime_version": "0.1.0",
                "package_version": "0.1.0",
                "package_sha256": package_sha256,
            },
            "target": {
                "name": "Zorin OS 17.3 representative laptop",
                "representative": True,
                "status": "passed",
            },
            "dimensions": [
                "restore_capability",
                "migration",
                "documentation",
                "provenance",
            ],
            "evidence": {
                "local_tests": 143,
                "source_validation": "passed",
                "package_lifecycle": "passed",
                "references": ["representative acceptance fixture"],
            },
            "acceptance": {
                "target_runtime_status": "passed",
                "exact_revision_accepted": True,
                "everkeep_integration_promoted": promoted,
                "everkeep_ready_promoted": promoted,
                "freshness_rule": "Exact 0.1.0 source, source tree, package version, package SHA-256, and target only.",
            },
        }

    def _continuity_paths(self, root: Path) -> tuple[Path, Path, Path]:
        return (
            root / "package" / "build-provenance.json",
            root / "representative" / "representative-target.json",
            root / "everkeep" / "goreecloud-care.target-runtime.json",
        )

    def test_continuity_requires_exact_representative_target_acceptance(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            provenance, representative, everkeep = self._continuity_paths(root)
            self._write_secure_json(provenance, self._build_provenance())

            payload = build_continuity_status(
                NOW,
                provenance_path=provenance,
                representative_acceptance_path=representative,
                everkeep_acceptance_path=everkeep,
                expected_uid=os.geteuid(),
            )
            self.assertEqual(payload["state"], "attention")
            self.assertEqual(payload["stage"], "target-acceptance-required")
            self.assertTrue(payload["required_evidence"])
            self.assertNotIn("freshness", payload)
            self.assertIn("rollback", payload["reason"].lower())

    def test_care_target_acceptance_cannot_self_promote_everkeep(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            provenance, representative, everkeep = self._continuity_paths(root)
            self._write_secure_json(provenance, self._build_provenance())
            self._write_secure_json(representative, self._acceptance_record())

            payload = build_continuity_status(
                NOW,
                provenance_path=provenance,
                representative_acceptance_path=representative,
                everkeep_acceptance_path=everkeep,
                expected_uid=os.geteuid(),
            )
            self.assertEqual(payload["state"], "attention")
            self.assertEqual(payload["stage"], "target-accepted-governance-pending")
            self.assertIn("cannot grant Everkeep readiness", payload["limitations"][0])
            self.assertEqual(payload["evidence_reference"], f"file://{representative}")

    def test_continuity_ready_requires_separate_promoted_everkeep_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            provenance, representative, everkeep = self._continuity_paths(root)
            self._write_secure_json(provenance, self._build_provenance())
            self._write_secure_json(representative, self._acceptance_record())
            self._write_secure_json(everkeep, self._acceptance_record(promoted=True))

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
            self.assertEqual(payload["limitations"], [])
            self.assertEqual(payload["evidence_reference"], f"file://{everkeep}")

    def test_continuity_rejects_promoted_record_with_different_package_sha(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            provenance, representative, everkeep = self._continuity_paths(root)
            self._write_secure_json(provenance, self._build_provenance())
            self._write_secure_json(representative, self._acceptance_record())
            self._write_secure_json(
                everkeep,
                self._acceptance_record(package_sha256="d" * 64, promoted=True),
            )

            payload = build_continuity_status(
                NOW,
                provenance_path=provenance,
                representative_acceptance_path=representative,
                everkeep_acceptance_path=everkeep,
                expected_uid=os.geteuid(),
            )
            self.assertEqual(payload["state"], "attention")
            self.assertEqual(payload["stage"], "target-accepted-governance-pending")
            self.assertIn("package SHA-256", payload["limitations"][0])

    def test_continuity_rejects_source_mismatch(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            provenance, representative, everkeep = self._continuity_paths(root)
            self._write_secure_json(provenance, self._build_provenance())
            self._write_secure_json(
                representative,
                self._acceptance_record(source_revision="e" * 40),
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

    def test_continuity_rejects_writable_or_malformed_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            provenance, representative, everkeep = self._continuity_paths(root)
            self._write_secure_json(provenance, self._build_provenance())
            self._write_secure_json(representative, self._acceptance_record())
            representative.chmod(0o666)

            writable = build_continuity_status(
                NOW,
                provenance_path=provenance,
                representative_acceptance_path=representative,
                everkeep_acceptance_path=everkeep,
                expected_uid=os.geteuid(),
            )
            self.assertEqual(writable["state"], "attention")
            self.assertEqual(writable["stage"], "target-acceptance-required")

            representative.write_text("{not-json\n", encoding="utf-8")
            representative.chmod(0o644)
            malformed = build_continuity_status(
                NOW,
                provenance_path=provenance,
                representative_acceptance_path=representative,
                everkeep_acceptance_path=everkeep,
                expected_uid=os.geteuid(),
            )
            self.assertEqual(malformed["state"], "attention")
            self.assertEqual(malformed["stage"], "target-acceptance-required")

    def test_render_json_is_machine_readable(self):
        payload = build_health_status(NOW)
        self.assertEqual(json.loads(render_json(payload)), payload)


if __name__ == "__main__":
    unittest.main()
