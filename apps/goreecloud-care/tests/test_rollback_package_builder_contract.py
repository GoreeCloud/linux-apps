from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DEV17_SCRIPT = ROOT / "scripts" / "build-dev17-rollback-package.sh"
STABLE_SCRIPT = ROOT / "scripts" / "build-stable-0.1.0-rollback-package.sh"
STABLE_SHA = "819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160"


class RollbackPackageBuilderContractTests(unittest.TestCase):
    def test_builders_have_valid_posix_shell_syntax(self) -> None:
        subprocess.run(["sh", "-n", str(DEV17_SCRIPT)], check=True)
        subprocess.run(["sh", "-n", str(STABLE_SCRIPT)], check=True)

    def test_historical_dev17_builder_remains_pinned_for_audit_context(self) -> None:
        source = DEV17_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            'DEV17_REVISION="0fda6f90a545eaf3d1bed525aae98c6529ebbf7b"',
            source,
        )
        self.assertIn('EXPECTED_VERSION="0.1.0~dev17"', source)
        self.assertIn('purpose=representative-development-rollback', source)

    def test_active_0_2_rollback_builder_is_pinned_to_immutable_stable_0_1_0(self) -> None:
        source = STABLE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            'STABLE_REVISION="bbc4779454c2887b810aa0ddc9e8a686a4c68ebd"',
            source,
        )
        self.assertIn('EXPECTED_VERSION="0.1.0"', source)
        self.assertIn(f'EXPECTED_SHA256="{STABLE_SHA}"', source)
        self.assertIn('git -C "$REPO_ROOT" cat-file -e "$STABLE_REVISION^{commit}"', source)
        self.assertIn('git -C "$REPO_ROOT" worktree add --detach "$WORKTREE" "$STABLE_REVISION"', source)
        self.assertIn('actual_sha=$(sha256sum "$EXPECTED_PACKAGE"', source)
        self.assertIn('[ "$actual_sha" = "$EXPECTED_SHA256" ]', source)

    def test_stable_builder_does_not_install_or_invoke_maintenance(self) -> None:
        source = STABLE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn(
            "does not install/remove packages, invoke Care cleanup, or access the network",
            source,
        )
        for forbidden in (
            "sudo ",
            "apt install",
            "apt remove",
            "pkexec ",
            "goreecloud-care-helper ",
            "goreecloud-care --",
            "git fetch",
            "git pull",
        ):
            self.assertNotIn(forbidden, source)

    def test_stable_builder_records_checksum_source_and_purpose(self) -> None:
        source = STABLE_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('sha256sum "$EXPECTED_PACKAGE"', source)
        self.assertIn("source_revision=$STABLE_REVISION", source)
        self.assertIn("package_version=$EXPECTED_VERSION", source)
        self.assertIn("package_sha256=$EXPECTED_SHA256", source)
        self.assertIn("purpose=stable-0.1.0-rollback-for-0.2-development", source)


if __name__ == "__main__":
    unittest.main()
