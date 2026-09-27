from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
BUILD = (ROOT / "scripts" / "build-deb.sh").read_text(encoding="utf-8")
VERIFY = (ROOT / "scripts" / "verify-reproducible-package.sh").read_text(encoding="utf-8")
WORKFLOW = (ROOT.parents[1] / ".github" / "workflows" / "care-ci.yml").read_text(encoding="utf-8")


class ReproduciblePackagingContractTests(unittest.TestCase):
    def test_build_uses_source_date_epoch_not_wall_clock(self):
        self.assertIn('SOURCE_DATE_EPOCH', BUILD)
        self.assertIn('git -C "$REPO_ROOT" show -s --format=%ct HEAD', BUILD)
        self.assertIn('export SOURCE_DATE_EPOCH', BUILD)
        self.assertNotIn('date +%s', BUILD)

    def test_build_normalizes_staged_mtimes(self):
        self.assertIn('find "$STAGE" -exec touch -h -d "@$SOURCE_DATE_EPOCH" {} +', BUILD)
        self.assertIn('dpkg-deb --root-owner-group', BUILD)

    def test_build_normalizes_umask_sensitive_modes(self):
        self.assertIn('find "$STAGE" -type d -exec chmod 0755 {} +', BUILD)
        self.assertIn('chmod 0644 "$STAGE/DEBIAN/control"', BUILD)
        self.assertIn('chmod 0644 "$STAGE/usr/lib/goreecloud-care/goreecloud_care.pth"', BUILD)
        self.assertIn('Caller umask is not part of package identity', BUILD)

    def test_build_eliminates_compressor_and_locale_variability(self):
        self.assertIn('export LC_ALL=C', BUILD)
        self.assertIn('export TZ=UTC', BUILD)
        self.assertIn('--deb-format=2.0', BUILD)
        self.assertIn('-Znone', BUILD)
        self.assertNotIn('-Zxz', BUILD)
        self.assertNotIn('-Zzstd', BUILD)

    def test_build_rejects_dirty_or_untracked_package_inputs(self):
        self.assertIn('git -C "$REPO_ROOT" diff --quiet -- apps/goreecloud-care', BUILD)
        self.assertIn('git -C "$REPO_ROOT" diff --cached --quiet -- apps/goreecloud-care', BUILD)
        self.assertIn('git -C "$REPO_ROOT" ls-files --error-unmatch', BUILD)
        self.assertIn('Package input is not part of the exact committed Care source', BUILD)
        self.assertIn('"$ROOT/goreecloud_care/"*.py', BUILD)

    def test_build_embeds_exact_source_provenance_without_circular_package_hash(self):
        self.assertIn('/usr/share/goreecloud-care/build-provenance.json', BUILD)
        self.assertIn('SOURCE_REVISION=$(git -C "$REPO_ROOT" rev-parse HEAD)', BUILD)
        self.assertIn('SOURCE_TREE=$(git -C "$REPO_ROOT" rev-parse HEAD:apps/goreecloud-care)', BUILD)
        self.assertIn('"source_revision": revision', BUILD)
        self.assertIn('"source_tree": tree', BUILD)
        self.assertIn('"package_sha256_embedded": False', BUILD)
        self.assertIn("embedding a package's own hash is circular", BUILD)

    def test_artifact_package_identity_is_exact(self):
        self.assertIn('VERSION="0.1.0"', BUILD)
        self.assertIn('RUNTIME_VERSION="0.1.0"', BUILD)
        self.assertIn('packaging/com.goreecloud.care.desktop', BUILD)
        self.assertIn('packaging/com.goreecloud.care.metainfo.xml', BUILD)
        self.assertIn('PACKAGE_NAME="goreecloud-care_0.1.0_all.deb"', VERIFY)
        self.assertNotIn('goreecloud-care_0.1.0~dev22_all.deb', VERIFY)

    def test_verifier_compares_independent_build_to_reference(self):
        self.assertIn('SOURCE_DATE_EPOCH="$SOURCE_DATE_EPOCH" sh "$ROOT/scripts/build-deb.sh"', VERIFY)
        self.assertIn('cmp -s "$REFERENCE" "$rebuilt"', VERIFY)
        self.assertIn('sha256sum "$REFERENCE"', VERIFY)
        self.assertIn('Reproducible package verification: passed', VERIFY)

    def test_verifier_exercises_different_umasks(self):
        self.assertIn('umask 0022', VERIFY)
        self.assertIn('umask 0002', VERIFY)
        self.assertIn('cmp -s "$REBUILT_022" "$REBUILT_002"', VERIFY)
        self.assertIn('Umask independence: passed (0022 == 0002)', VERIFY)

    def test_ci_runs_same_environment_reproducibility_gate(self):
        self.assertIn('name: GoreeCloud Care 0.1.0 Stable Artifact Qualification', WORKFLOW)
        self.assertIn('goreecloud-care_0.1.0_all.deb', WORKFLOW)
        self.assertIn('lifecycle=release-candidate', WORKFLOW)
        self.assertIn('artifact_version=0.1.0', WORKFLOW)
        self.assertIn('stable_promotion_authorized=false', WORKFLOW)
        self.assertIn('Verify reproducible GoreeCloud Care package', WORKFLOW)

    def test_ci_compares_jammy_and_noble_package_bytes(self):
        self.assertIn('ubuntu-22.04', WORKFLOW)
        self.assertIn('ubuntu-24.04', WORKFLOW)
        self.assertIn('Compare cross-environment package bytes', WORKFLOW)
        self.assertIn('cmp -s "$JAMMY" "$NOBLE"', WORKFLOW)
        self.assertIn('cross_environment_reproducibility=passed', WORKFLOW)


if __name__ == "__main__":
    unittest.main()
