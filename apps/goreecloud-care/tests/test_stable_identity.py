from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
STABLE_SOURCE = "bbc4779454c2887b810aa0ddc9e8a686a4c68ebd"
STABLE_PACKAGE_SHA = "819cff6e0132bf6b09df0986682995c25b14c39e74982f725efd0b5a21b71160"


class DevelopmentArtifactIdentityTests(unittest.TestCase):
    def test_platform_manifest_declares_nonconformant_dev3_contract_0_2_line(self) -> None:
        manifest = (ROOT / "goreecloud.platform.yaml").read_text(encoding="utf-8")
        self.assertIn('schema_version: "0.2"', manifest)
        self.assertIn("\nlifecycle: development\n", manifest)
        self.assertIn("version: 0.2.0-dev3", manifest)
        self.assertIn("status: nonconformant", manifest)
        self.assertIn('platform_contract: "0.2"', manifest)
        self.assertIn('glaze_ui_required: "1.4.1"', manifest)
        self.assertNotIn("\nlifecycle: stable\n", manifest)

    def test_platform_manifest_has_exactly_seven_integral_systems_and_sync_is_separate(self) -> None:
        manifest = (ROOT / "goreecloud.platform.yaml").read_text(encoding="utf-8")
        for system in (
            "manager",
            "privacy_shield",
            "wardveil_security",
            "everkeep",
            "glaze_ui",
            "mesh",
            "identity",
        ):
            self.assertIn(f"\n  {system}:\n", manifest)
        self.assertNotIn("\n  sync:\n", manifest)
        self.assertIn("GoreeCloud Sync is separately governed application/service functionality", manifest)

    def test_runtime_and_python_metadata_are_dev3_development_identity(self) -> None:
        init_source = (ROOT / "goreecloud_care" / "__init__.py").read_text(encoding="utf-8")
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        self.assertIn('__version__ = "0.2.0-dev3"', init_source)
        self.assertIn('version = "0.2.0-dev3"', pyproject)
        self.assertIn('Development Status :: 3 - Alpha', pyproject)
        self.assertNotIn('Development Status :: 5 - Production/Stable', pyproject)

    def test_core_gtk_identity_is_canonical_and_v14_family_specific(self) -> None:
        source = (ROOT / "goreecloud_care" / "app.py").read_text(encoding="utf-8")
        self.assertIn('APP_ID = "com.goreecloud.care"', source)
        self.assertIn('title="GoreeCloud Care"', source)
        self.assertIn('from .glaze_v14 import layout_environment', source)
        self.assertIn('self.header_subtitle = "Local maintenance • Glaze UI V1.4"', source)
        self.assertNotIn('Adaptive Resonance preview', source)

    def test_current_machine_glaze_authority_is_v141_optical_intelligence(self) -> None:
        source = (ROOT / "goreecloud_care" / "glaze_v14.py").read_text(encoding="utf-8")
        self.assertIn('GLAZE_UI_LABEL = "GLAZE UI V1.4 — Optical Intelligence"', source)
        self.assertIn('GLAZE_UI_TARGET_VERSION = "1.4.1"', source)
        self.assertIn('GLAZE_UI_SOURCE_REVISION = "4fab9da0fad2e5c974e0e66ec88632c61745751c"', source)
        self.assertIn('GLAZE_UI_SOURCE_QUALIFICATION_ANCHOR = "66478aed461b83c49b2ed027c3e4afc26520e98c"', source)
        self.assertIn('GLAZE_UI_PREVIOUS_BASELINE = "1.4.0"', source)
        self.assertNotIn('Form-Factor Evolution', source)

    def test_insights_identity_remains_canonical_and_lifecycle_neutral(self) -> None:
        source = (ROOT / "goreecloud_care" / "insights_window.py").read_text(encoding="utf-8")
        self.assertIn('APP_ID = "com.goreecloud.care.insights"', source)
        self.assertIn('self.header_subtitle = "Read-only local review"', source)
        self.assertNotIn('Release Candidate •', source)

    def test_appstream_preserves_stable_history_and_adds_dev3_development(self) -> None:
        desktop_path = ROOT / "packaging" / "com.goreecloud.care.desktop"
        metainfo_path = ROOT / "packaging" / "com.goreecloud.care.metainfo.xml"
        desktop = desktop_path.read_text(encoding="utf-8")
        metainfo = metainfo_path.read_text(encoding="utf-8")
        self.assertIn("Name=GoreeCloud Care", desktop)
        self.assertIn("StartupWMClass=com.goreecloud.care", desktop)
        self.assertIn("<id>com.goreecloud.care</id>", metainfo)
        self.assertIn('<release version="0.2.0-dev3" date="2026-09-15" type="development"/>', metainfo)
        self.assertIn('<release version="0.1.0" date="2026-09-07" type="stable"/>', metainfo)

    def test_package_build_uses_distinct_dev3_artifact_identity(self) -> None:
        build = (ROOT / "scripts" / "build-deb.sh").read_text(encoding="utf-8")
        self.assertIn('VERSION="0.2.0~dev3"', build)
        self.assertIn('RUNTIME_VERSION="0.2.0-dev3"', build)
        self.assertIn("Description: GoreeCloud Care local-first maintenance utility", build)
        self.assertIn("packaging/com.goreecloud.care.desktop", build)
        self.assertIn("packaging/com.goreecloud.care.metainfo.xml", build)
        self.assertNotIn('VERSION="0.1.0"', build)

    def test_platform_status_package_identity_matches_candidate(self) -> None:
        source = (ROOT / "goreecloud_care" / "platform_status.py").read_text(encoding="utf-8")
        self.assertIn('PACKAGE_VERSION = "0.2.0~dev3"', source)
        self.assertNotIn('PACKAGE_VERSION = "0.1.0"', source)

    def test_stable_0_1_0_acceptance_is_retained_as_historical_only(self) -> None:
        release = (ROOT / "RELEASE-ACCEPTANCE.md").read_text(encoding="utf-8")
        manifest = (ROOT / "goreecloud.platform.yaml").read_text(encoding="utf-8")
        self.assertIn("immutable **Stable `0.1.0` acceptance record**", release)
        self.assertIn(STABLE_SOURCE, release)
        self.assertIn(STABLE_PACKAGE_SHA, release)
        self.assertIn(STABLE_SOURCE, manifest)
        self.assertIn(STABLE_PACKAGE_SHA, manifest)
        self.assertIn("Historical Stable 0.1.0", manifest)

    def test_dev3_does_not_inherit_external_platform_acceptance(self) -> None:
        manifest = (ROOT / "goreecloud.platform.yaml").read_text(encoding="utf-8")
        for system in ("privacy_shield", "wardveil_security", "everkeep"):
            self.assertIn(f"  {system}:\n    result: applicable-nonconformant", manifest)
        self.assertIn("  glaze_ui:\n    result: applicable-migration-required", manifest)
        self.assertIn("Stable promotion requires a later explicit exact-candidate decision", manifest)
        self.assertIn("cannot be inferred from historical 0.1.0, dev1, dev2, or prior 1.4.0 evidence", manifest)

    def test_local_status_producers_still_do_not_self_assign_external_governance(self) -> None:
        platform_status = (ROOT / "goreecloud_care" / "platform_status.py").read_text(encoding="utf-8")
        self.assertIn('"protected_by_wardveil": False', platform_status)
        self.assertIn('production_approved: bool = False', platform_status)

    def test_ci_is_v141_candidate_qualification_not_stable_republication(self) -> None:
        workflow = (REPO_ROOT / ".github" / "workflows" / "care-ci.yml").read_text(encoding="utf-8")
        self.assertIn("name: GoreeCloud Care 0.2.0-dev3 Glaze UI V1.4.1 Optical Intelligence Qualification", workflow)
        self.assertIn("goreecloud-care_0.2.0~dev3_all.deb", workflow)
        self.assertIn("lifecycle=development", workflow)
        self.assertIn("glaze_ui_target=1.4.1", workflow)
        self.assertIn("platform_contract=0.2", workflow)
        self.assertIn("stable_promotion_authorized=false", workflow)
        self.assertIn("build-stable-0.1.0-rollback-package.sh", workflow)


if __name__ == "__main__":
    unittest.main()
