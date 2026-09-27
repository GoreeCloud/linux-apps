from __future__ import annotations

import subprocess
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "build-dev17-rollback-package.sh"


class RollbackPackageBuilderContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.source = SCRIPT.read_text(encoding="utf-8")

    def test_builder_has_valid_posix_shell_syntax(self) -> None:
        subprocess.run(["sh", "-n", str(SCRIPT)], check=True)

    def test_builder_is_pinned_to_accepted_dev17_archive(self) -> None:
        self.assertIn(
            'DEV17_SOURCE_REVISION="0fda6f90a545eaf3d1bed525aae98c6529ebbf7b"',
            self.source,
        )
        self.assertIn(
            'DEV17_ARCHIVE_REVISION="1a57ccd9b3311000c99e273877eff1af06b06b38"',
            self.source,
        )
        self.assertIn(
            'DEV17_ARCHIVE_TREE="7168db501e9e2fd7ce23496f607ffe958ab4c835"',
            self.source,
        )
        self.assertIn('EXPECTED_VERSION="0.1.0~dev17"', self.source)
        self.assertIn(
            'git -C "$REPO_ROOT" cat-file -e "$DEV17_ARCHIVE_REVISION^{commit}"',
            self.source,
        )
        self.assertIn(
            'git -C "$REPO_ROOT" worktree add --detach "$WORKTREE" "$DEV17_ARCHIVE_REVISION"',
            self.source,
        )
        self.assertIn(
            'actual_archive_tree=$(git -C "$REPO_ROOT" rev-parse "$DEV17_ARCHIVE_REVISION^{tree}")',
            self.source,
        )

    def test_builder_does_not_install_or_invoke_maintenance(self) -> None:
        self.assertIn(
            "does not install/remove packages, invoke Care cleanup, or access the network",
            self.source,
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
            self.assertNotIn(forbidden, self.source)

    def test_builder_records_checksum_and_provenance(self) -> None:
        self.assertIn('sha256sum "$EXPECTED_PACKAGE"', self.source)
        self.assertIn("source_revision=$DEV17_SOURCE_REVISION", self.source)
        self.assertIn("archive_revision=$DEV17_ARCHIVE_REVISION", self.source)
        self.assertIn("archive_tree=$DEV17_ARCHIVE_TREE", self.source)
        self.assertIn("package_version=$EXPECTED_VERSION", self.source)
        self.assertIn("purpose=representative-development-rollback", self.source)


if __name__ == "__main__":
    unittest.main()
