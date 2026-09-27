from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]


class StableArtifactIdentityTests(unittest.TestCase):
    def test_platform_manifest_keeps_governed_rc_lifecycle_for_0_1_0_artifact(self) -> None:
        manifest = (ROOT / "goreecloud.platform.yaml").read_text(encoding="utf-8")
        self.assertIn("lifecycle: release-candidate", manifest)
        self.assertIn("version: 0.1.0", manifest)
        self.assertIn("status: nonconformant", manifest)
        self.assertNotIn("lifecycle: stable", manifest)
        self.assertNotIn("version: 0.1.0-dev22", manifest)

    def test_runtime_and_python_metadata_are_final_0_1_0_artifact_identity(self) -> None:
        init_source = (ROOT / "goreecloud_care" / "__init__.py").read_text(encoding="utf-8")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('__version__ = "0.1.0"', init_source)
        self.assertIn('version = "0.1.0"', pyproject)
        self.assertIn('Development Status :: 5 - Production/Stable', pyproject)
        self.assertNotIn('0.1.0-dev22', init_source)

    def test_core_gtk_identity_is_canonical_and_lifecycle_neutral(self) -> None:
        source = (ROOT / "goreecloud_care" / "app.py").read_text(encoding="utf-8")
        self.assertIn('APP_ID = "com.goreecloud.care"', source)
        self.assertIn('title="GoreeCloud Care"', source)
        self.assertIn('self.header_subtitle = "Local maintenance • Adaptive Resonance preview"', source)
        self.assertNotIn('GoreeCloud Care — Release Candidate', source)
        self.assertNotIn('Release Candidate •', source)

    def test_insights_identity_is_canonical_and_lifecycle_neutral(self) -> None:
        source = (ROOT / "goreecloud_care" / "insights_window.py").read_text(encoding="utf-8")
        self.assertIn('APP_ID = "com.goreecloud.care.insights"', source)
        self.assertIn('self.header_subtitle = "Read-only local review"', source)
        self.assertNotIn('Release Candidate •', source)

    def test_desktop_and_appstream_sources_are_canonical_0_1_0(self) -> None:
        desktop_path = ROOT / "packaging" / "com.goreecloud.care.desktop"
        metainfo_path = ROOT / "packaging" / "com.goreecloud.care.metainfo.xml"
        self.assertTrue(desktop_path.is_file())
        self.assertTrue(metainfo_path.is_file())
        self.assertFalse((ROOT / "packaging" / "com.goreecloud.care.dev.desktop").exists())
        self.assertFalse((ROOT / "packaging" / "com.goreecloud.care.dev.metainfo.xml").exists())
        desktop = desktop_path.read_text(encoding="utf-8")
        metainfo = metainfo_path.read_text(encoding="utf-8")
        self.assertIn("Name=GoreeCloud Care", desktop)
        self.assertNotIn("Release Candidate", desktop)
        self.assertIn("StartupWMClass=com.goreecloud.care", desktop)
        self.assertIn("<id>com.goreecloud.care</id>", metainfo)
        self.assertIn("<name>GoreeCloud Care</name>", metainfo)
        self.assertIn('<release version="0.1.0" date="2026-09-07" type="stable"/>', metainfo)

    def test_package_build_uses_final_artifact_identity(self) -> None:
        build = (ROOT / "scripts" / "build-deb.sh").read_text(encoding="utf-8")
        self.assertIn('VERSION="0.1.0"', build)
        self.assertIn('RUNTIME_VERSION="0.1.0"', build)
        self.assertIn("Description: GoreeCloud Care local-first maintenance utility", build)
        self.assertIn("packaging/com.goreecloud.care.desktop", build)
        self.assertIn("packaging/com.goreecloud.care.metainfo.xml", build)
        self.assertNotIn("packaging/com.goreecloud.care.dev.desktop", build)
        self.assertNotIn("packaging/com.goreecloud.care.dev.metainfo.xml", build)

    def test_platform_status_package_identity_matches_artifact(self) -> None:
        source = (ROOT / "goreecloud_care" / "platform_status.py").read_text(encoding="utf-8")
        self.assertIn('PACKAGE_VERSION = "0.1.0"', source)
        self.assertNotIn('PACKAGE_VERSION = "0.1.0~dev22"', source)

    def test_ci_and_representative_harnesses_are_artifact_qualification_not_promotion(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "care-ci.yml").read_text(encoding="utf-8")
        prepare = (ROOT / "scripts" / "prepare-representative-acceptance.sh").read_text(encoding="utf-8")
        runner = (ROOT / "scripts" / "run-representative-acceptance.sh").read_text(encoding="utf-8")
        self.assertIn("name: GoreeCloud Care 0.1.0 Stable Artifact Qualification", workflow)
        for text in (workflow, prepare, runner):
            self.assertIn("lifecycle=release-candidate", text)
            self.assertIn("artifact_version=0.1.0", text)
            self.assertIn("stable_promotion_authorized=false", text)
            self.assertNotIn("lifecycle=stable", text)

    def test_artifact_source_does_not_self_inherit_exact_rc_platform_governance(self) -> None:
        manifest = (ROOT / "goreecloud.platform.yaml").read_text(encoding="utf-8")
        self.assertIn("status: nonconformant", manifest)
        self.assertIn("0.1.0 golden artifact candidate requires exact-source", manifest)
        self.assertIn("productionEligible=false", manifest)
        self.assertIn("protected_by_wardveil=false", manifest)
        self.assertIn("Stable promotion must be an explicit governance action", manifest)


if __name__ == "__main__":
    unittest.main()
