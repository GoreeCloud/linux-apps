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
            "read-only/non-destructive 0.2.0-dev2 Glaze UI 2.2 representative acceptance evidence",
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

    def test_preparation_harness_requires_clean_exact_v22_candidate_source(self) -> None:
        self.assertIn('status --porcelain --untracked-files=no -- apps/goreecloud-care .github/workflows/care-ci.yml', self.source)
        self.assertIn('git -C "$REPO_ROOT" rev-parse HEAD', self.source)
        self.assertIn('EXPECTED_RUNTIME_VERSION="0.2.0-dev2"', self.source)
        self.assertIn('EXPECTED_PACKAGE_VERSION="0.2.0~dev2"', self.source)
        self.assertIn("requires lifecycle: development", self.source)
        self.assertIn("status: nonconformant", self.source)
        self.assertIn('glaze_ui_required: \"2.2.0\"', self.source)
        self.assertIn("stable_promotion_authorized=false", self.source)

    def test_preparation_harness_records_exact_source_and_package_provenance(self) -> None:
        self.assertIn('EXPECTED_PACKAGE="$ROOT/dist/goreecloud-care_${EXPECTED_PACKAGE_VERSION}_all.deb"', self.source)
        self.assertIn('sha256sum "$PACKAGE"', self.source)
        self.assertIn("source_revision=$SOURCE_REVISION", self.source)
        self.assertIn("package_sha256=$PACKAGE_SHA256", self.source)
        self.assertIn("lifecycle=development", self.source)
        self.assertIn('GLAZE_TARGET="2.2.0"', self.source)
        self.assertIn('GLAZE_RELEASE_TAG="v2.2.0"', self.source)
        self.assertIn('GLAZE_SOURCE_REVISION="6731098b28dd0393faa878c70d989a221d714a20"', self.source)
        self.assertIn("glaze_ui_target=$GLAZE_TARGET", self.source)
        self.assertIn("glaze_ui_release_tag=$GLAZE_RELEASE_TAG", self.source)
        self.assertIn("glaze_ui_source_revision=$GLAZE_SOURCE_REVISION", self.source)

    def test_preparation_harness_gates_installed_status_on_exact_runtime(self) -> None:
        self.assertIn('INSTALLED_PROBE_DIR=$(mktemp -d)', self.source)
        self.assertIn('if [ "$INSTALLED_RUNTIME" = "$EXPECTED_RUNTIME_VERSION" ]; then', self.source)
        self.assertIn("api_version=not-probed-runtime-mismatch", self.source)
        self.assertIn("candidate-only status snapshots were skipped", self.source)

    def test_manual_checklist_is_v22_and_new_candidate_specific(self) -> None:
        for required in (
            "Glaze UI 2.2 identity, System Shell, and composition",
            "Compact window preserves all maintenance tasks",
            "Narrow Desktop uses a readable single-column composition",
            "Desktop uses the intended canonical Care composition",
            "Wide Desktop adds breathing room/hierarchy",
            "Orca/AT-SPI scan, completion, cancellation, failure",
            "Light appearance is readable and stable",
            "Dark appearance is readable and stable",
            "Deep Dark appearance is readable and stable",
            "GTK HighContrast/system palette authority is respected",
            "Stable-0.1.0-downgrade/0.2.0~dev2-restore/final-state",
            "Glaze UI 2.2 exact-candidate human/native consumer review",
            "Privacy Shield exact-dev2",
            "Wardveil exact-dev2",
            "Everkeep exact-dev2",
            "Platform Contract exact-dev2",
        ):
            self.assertIn(required, self.source)
        self.assertNotIn("Glaze UI V1.4 exact-candidate human/native consumer review", self.source)

    def test_preparation_harness_uses_stable_0_1_0_as_rollback(self) -> None:
        self.assertIn("build-stable-0.1.0-rollback-package.sh", self.source)
        self.assertIn("goreecloud-care_0.1.0_all.deb", self.source)
        self.assertIn("819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160", self.source)
        self.assertNotIn("build-dev17-rollback-package.sh", self.source)

    def test_preparation_harness_never_self_promotes(self) -> None:
        self.assertIn("0.2.0-dev2 Glaze UI 2.2 representative acceptance preparation: passed", self.source)
        self.assertIn("Stable promotion authorized: false", self.source)
        self.assertNotIn("Stable promotion authorized: true", self.source)
        self.assertNotIn("lifecycle=stable", self.source)


if __name__ == "__main__":
    unittest.main()
