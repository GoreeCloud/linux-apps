from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "prepare-representative-acceptance.sh"


class RepresentativeAcceptanceContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = SCRIPT.read_text(encoding="utf-8")

    def test_preparation_harness_has_valid_posix_shell_syntax(self) -> None:
        subprocess.run(["sh", "-n", str(SCRIPT)], check=True)

    def test_preparation_harness_is_non_destructive_and_unprivileged(self) -> None:
        self.assertIn(
            "read-only/non-destructive 0.1.0 golden artifact representative acceptance evidence",
            self.source,
        )
        self.assertIn(
            "does not invoke Care cleanup, PolicyKit, pkexec, sudo, apt, or network operations",
            self.source,
        )
        for forbidden in (
            "sudo apt ",
            "pkexec ",
            "apt remove ",
            "apt install ",
            "goreecloud-care-helper ",
        ):
            self.assertNotIn(forbidden, self.source)

    def test_preparation_harness_requires_clean_exact_golden_candidate_source(self) -> None:
        self.assertIn('git -C "$REPO_ROOT" status --porcelain --untracked-files=no', self.source)
        self.assertIn('git -C "$REPO_ROOT" rev-parse HEAD', self.source)
        self.assertIn('EXPECTED_RUNTIME_VERSION="0.1.0"', self.source)
        self.assertIn('EXPECTED_PACKAGE_VERSION="0.1.0"', self.source)
        self.assertIn("requires lifecycle: release-candidate", self.source)
        self.assertIn("status: nonconformant", self.source)
        self.assertIn("artifact_version=0.1.0", self.source)
        self.assertIn("stable_promotion_authorized=false", self.source)

    def test_preparation_harness_records_exact_source_and_package_provenance(self) -> None:
        self.assertIn('EXPECTED_PACKAGE="$ROOT/dist/goreecloud-care_${EXPECTED_PACKAGE_VERSION}_all.deb"', self.source)
        self.assertIn('sha256sum "$PACKAGE"', self.source)
        self.assertIn("source_revision=$SOURCE_REVISION", self.source)
        self.assertIn("package_sha256=$PACKAGE_SHA256", self.source)
        self.assertIn("lifecycle=release-candidate", self.source)

    def test_preparation_harness_gates_installed_status_on_exact_runtime(self) -> None:
        self.assertIn('INSTALLED_PROBE_DIR=$(mktemp -d)', self.source)
        self.assertIn('if [ "$INSTALLED_RUNTIME" = "$EXPECTED_RUNTIME_VERSION" ]; then', self.source)
        self.assertIn("api_version=not-probed-runtime-mismatch", self.source)
        self.assertIn("candidate-only status snapshots were skipped", self.source)

    def test_manual_checklist_keeps_artifact_delta_and_platform_gates_explicit(self) -> None:
        for required in (
            "0.1.0 identity delta",
            "Main window title is GoreeCloud Care",
            "Orca completion/cancellation/failure",
            "install/remove/reinstall/dev17-downgrade/0.1.0-restore/final-state",
            "Privacy Shield exact-0.1.0",
            "Wardveil exact-0.1.0",
            "Everkeep exact-0.1.0",
            "Glaze V1.2 exact-0.1.0",
            "V1.3 remains Proposed / consumer-ineligible",
        ):
            self.assertIn(required, self.source)

    def test_preparation_harness_never_self_promotes(self) -> None:
        self.assertIn("0.1.0 golden artifact representative acceptance preparation: passed", self.source)
        self.assertIn("Stable promotion authorized: false", self.source)
        self.assertNotIn("Stable promotion authorized: true", self.source)
        self.assertNotIn("lifecycle=stable", self.source)


if __name__ == "__main__":
    unittest.main()
