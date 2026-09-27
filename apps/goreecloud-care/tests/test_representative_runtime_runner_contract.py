from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "scripts" / "run-representative-acceptance.sh"


class RepresentativeRuntimeRunnerContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = RUNNER.read_text(encoding="utf-8")

    def test_runner_has_valid_posix_shell_syntax(self) -> None:
        subprocess.run(["sh", "-n", str(RUNNER)], check=True)

    def test_runner_is_pinned_to_representative_zorin_target_and_normal_user(self) -> None:
        self.assertIn('"$(id -u)" -ne 0', self.source)
        self.assertIn("Run representative acceptance as the normal Zorin desktop user, not as root", self.source)
        self.assertIn("Zorin OS 17.3", self.source)
        self.assertIn("PRETTY_NAME", self.source)

    def test_runner_requires_clean_exact_golden_candidate_source_and_tree(self) -> None:
        self.assertIn('status --porcelain --untracked-files=no -- apps/goreecloud-care .github/workflows/care-ci.yml', self.source)
        self.assertIn('SOURCE_REVISION=$(git -C "$REPO_ROOT" rev-parse HEAD)', self.source)
        self.assertIn('SOURCE_TREE=$(git -C "$REPO_ROOT" rev-parse HEAD:apps/goreecloud-care)', self.source)
        self.assertIn('EXPECTED_RUNTIME_VERSION="0.1.0"', self.source)
        self.assertIn('EXPECTED_PACKAGE_VERSION="0.1.0"', self.source)
        self.assertIn("requires lifecycle: release-candidate", self.source)
        self.assertIn("status: nonconformant", self.source)

    def test_runner_executes_all_automatable_exact_candidate_gates(self) -> None:
        for required in (
            'sh ./scripts/validate.sh',
            'sh ./scripts/build-deb.sh dist',
            'sh ./scripts/verify-reproducible-package.sh "$CANDIDATE"',
            'sh ./scripts/build-dev17-rollback-package.sh "$ROLLBACK_DIR"',
            'sh ./scripts/validate-package-lifecycle.sh "$CANDIDATE" "$ROLLBACK"',
            'sha256sum "$CANDIDATE"',
            'dpkg-query -W',
            'goreecloud-care --version',
        ):
            self.assertIn(required, self.source)
        self.assertIn("Representative package install/remove/reinstall/downgrade/rollback acceptance: passed", self.source)
        self.assertIn("Reproducible package verification: passed", self.source)

    def test_runner_generates_schema_compatible_target_handoff_without_promotion(self) -> None:
        for required in (
            '"schema_version": 1',
            '"application": "GoreeCloud Care"',
            '"producer": "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care"',
            '"restore_capability"',
            '"migration"',
            '"documentation"',
            '"provenance"',
            '"target_runtime_status": "passed"',
            '"exact_revision_accepted": True',
            '"everkeep_integration_promoted": False',
            '"everkeep_ready_promoted": False',
        ):
            self.assertIn(required, self.source)
        self.assertIn("lifecycle=release-candidate", self.source)
        self.assertIn("artifact_version=0.1.0", self.source)
        self.assertIn("stable_promotion_authorized=false", self.source)

    def test_runner_installs_only_care_owned_root_protected_target_record(self) -> None:
        self.assertIn(
            'REPRESENTATIVE_RECORD="/var/lib/goreecloud-care/acceptance/representative-target.json"',
            self.source,
        )
        self.assertIn('sudo install -d -o root -g root -m 0755 /var/lib/goreecloud-care/acceptance', self.source)
        self.assertIn('sudo install -o root -g root -m 0644 "$OUT/representative-target.json" "$REPRESENTATIVE_RECORD"', self.source)
        self.assertNotIn('/var/lib/goreecloud/everkeep/acceptance/goreecloud-care.target-runtime.json', self.source)

    def test_runner_proves_care_target_record_cannot_self_promote(self) -> None:
        self.assertIn('everkeep_acceptance_path="/nonexistent/goreecloud-care-everkeep.json"', self.source)
        self.assertIn('assert payload["state"] == "attention"', self.source)
        self.assertIn('assert payload["stage"] == "target-accepted-governance-pending"', self.source)
        self.assertIn("Everkeep promotion: not performed by this runner", self.source)

    def test_runner_reports_golden_artifact_acceptance_without_stable_claim(self) -> None:
        self.assertIn("Representative 0.1.0 golden artifact target acceptance: passed", self.source)
        self.assertIn("Stable promotion authorized: false", self.source)
        self.assertIn("remains Release Candidate / nonconformant", self.source)
        self.assertNotIn("Stable / conformant", self.source)

    def test_runner_never_invokes_care_cleanup_actions(self) -> None:
        for forbidden in (
            "goreecloud-care --clean",
            "goreecloud-care --empty-trash",
            "goreecloud-care --reclaim",
            "goreecloud-care-helper clean",
        ):
            self.assertNotIn(forbidden, self.source)
        self.assertIn("never invokes a Care cleanup action", self.source)


if __name__ == "__main__":
    unittest.main()
