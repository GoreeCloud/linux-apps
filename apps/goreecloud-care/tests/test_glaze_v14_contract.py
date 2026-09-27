from __future__ import annotations

from pathlib import Path
import unittest

from goreecloud_care.glaze_v14_optical import (
    GLAZE_OPTICAL_ENGINE_V14_1,
    MAX_MEMORY_TINT_INFLUENCE,
    accept_performance_level,
    care_default_optical_state,
    optical_css_classes,
    resolve_glaze_optics,
    resolve_glaze_optics_v141,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "goreecloud_care"


def _source(name: str) -> str:
    return (PACKAGE / name).read_text(encoding="utf-8")


class _Adapter:
    def __init__(self, payload=None, error: Exception | None = None) -> None:
        self.payload = payload
        self.error = error

    def resolve(self):
        if self.error is not None:
            raise self.error
        return self.payload


class GlazeV14ContractTests(unittest.TestCase):
    def test_v14_declares_current_optical_intelligence_authority(self) -> None:
        source = _source("glaze_v14.py")
        self.assertIn('GLAZE_UI_LABEL = "GLAZE UI V1.4 — Optical Intelligence"', source)
        self.assertIn('GLAZE_UI_TARGET_VERSION = "1.4.1"', source)
        self.assertIn(
            'GLAZE_UI_SOURCE_REVISION = "4fab9da0fad2e5c974e0e66ec88632c61745751c"',
            source,
        )
        self.assertIn(
            'GLAZE_UI_SOURCE_QUALIFICATION_ANCHOR = "66478aed461b83c49b2ed027c3e4afc26520e98c"',
            source,
        )
        self.assertIn('GLAZE_UI_PREVIOUS_BASELINE = "1.4.0"', source)
        self.assertIn('GLAZE_UI_ADOPTION_STATE = "development"', source)
        self.assertIn("GLAZE_UI_CONSUMER_ELIGIBLE = False", source)

    def test_v14_is_additive_to_v13_but_not_defined_by_form_factor(self) -> None:
        source = _source("glaze_v14.py")
        self.assertIn("CSS as V13_CSS", source)
        self.assertIn('CSS = V13_CSS + b"\\n" + V14_CSS', source)
        self.assertIn("Optical Intelligence", source)
        self.assertIn("application-owned GTK", source)
        self.assertNotIn('GLAZE_UI_LABEL = "GLAZE UI V1.4 — Form-Factor Evolution"', source)

    def test_optical_engine_is_local_and_deterministic(self) -> None:
        source = _source("glaze_v14_optical.py")
        self.assertIn("does not collect environmental signals", source)
        self.assertIn('"telemetry_required": False', source)
        self.assertIn('"remote_context_required": False', source)
        self.assertNotIn("requests.", source)
        self.assertNotIn("subprocess", source)

    def test_default_optics_match_v14_foundation_bounds(self) -> None:
        state = resolve_glaze_optics({"appearance":"light","backgroundComplexity":"unknown","backgroundLuminance":"bright","semanticImportance":0.80})
        self.assertEqual(state.mode, "adaptive-optical")
        self.assertAlmostEqual(state.frost_strength, 0.5566, places=4)
        self.assertAlmostEqual(state.semantic_protection, 0.868, places=4)
        self.assertAlmostEqual(state.blur_scale, 0.63544, places=5)
        self.assertTrue(state.decorative_tint_allowed)

    def test_reduced_transparency_forces_solid_accessible(self) -> None:
        state = resolve_glaze_optics({"memoryTint":{"css":"#abcdef","influence":0.08},"accessibility":{"reducedTransparency":True}})
        self.assertEqual(state.mode, "solid-accessible")
        self.assertEqual(state.blur_scale, 0.0)
        self.assertEqual(state.semantic_protection, 1.0)
        self.assertIsNone(state.memory_tint)
        self.assertFalse(state.decorative_tint_allowed)
        self.assertEqual(optical_css_classes(state), ("optical-solid-accessible",))

    def test_increased_contrast_suppresses_decorative_tint_and_warmth(self) -> None:
        state = resolve_glaze_optics({"daypart":"dusk","memoryTint":{"css":"#abcdef","influence":1},"accessibility":{"increasedContrast":True}})
        self.assertIsNone(state.memory_tint)
        self.assertEqual(state.warmth, 0.0)
        self.assertFalse(state.decorative_tint_allowed)

    def test_memory_tint_is_bounded_to_eight_percent(self) -> None:
        state = resolve_glaze_optics({"memoryTint":{"css":"#abcdef","influence":99}})
        self.assertIsNotNone(state.memory_tint)
        assert state.memory_tint is not None
        self.assertEqual(MAX_MEMORY_TINT_INFLUENCE, 0.08)
        self.assertEqual(state.memory_tint.influence, 0.08)

    def test_malformed_context_fails_to_bounded_defaults(self) -> None:
        state = resolve_glaze_optics({"appearance":"invalid","backgroundComplexity":object(),"backgroundLuminance":None,"depth":"impossible","daypart":123,"baseFrost":"not-a-number"})
        self.assertEqual(state.appearance, "light")
        self.assertEqual(state.background_complexity, "unknown")
        self.assertEqual(state.depth, "base")
        self.assertGreaterEqual(state.frost_strength, 0.20)
        self.assertLessEqual(state.frost_strength, 0.88)

    def test_v141_adapter_exception_fails_safe_and_cannot_be_overridden(self) -> None:
        resolution = resolve_glaze_optics_v141(
            signal_adapter=_Adapter(error=RuntimeError("private adapter detail")),
            overrides={"memoryTint":{"css":"#abcdef","influence":0.08},"accessibility":{"forcedColors":False,"reducedTransparency":False}},
        )
        self.assertEqual(resolution.adapter_status, "failed-safe")
        self.assertEqual(resolution.state.mode, "solid-accessible")
        self.assertTrue(resolution.state.accessibility.forced_colors)
        self.assertTrue(resolution.state.accessibility.reduced_transparency)
        self.assertEqual(resolution.state.blur_scale, 0.0)
        self.assertIsNone(resolution.state.memory_tint)
        self.assertNotIn("private adapter detail", repr(resolution))

    def test_v141_optional_error_observer_cannot_break_fallback(self) -> None:
        seen: list[str] = []
        def observer(exc: Exception) -> None:
            seen.append(type(exc).__name__)
            raise RuntimeError("observer failure")
        resolution = resolve_glaze_optics_v141(signal_adapter=_Adapter(error=ValueError("adapter failed")), on_adapter_error=observer)
        self.assertEqual(seen, ["ValueError"])
        self.assertEqual(resolution.adapter_status, "failed-safe")
        self.assertEqual(resolution.state.mode, "solid-accessible")

    def test_v141_no_adapter_keeps_normal_local_resolution(self) -> None:
        resolution = resolve_glaze_optics_v141(overrides={"appearance":"dark","semanticImportance":0.8})
        self.assertEqual(resolution.adapter_status, "not-configured")
        self.assertEqual(resolution.state.mode, "adaptive-optical")
        self.assertEqual(resolution.state.appearance, "dark")

    def test_v141_performance_governance_is_downgrade_only(self) -> None:
        accepted, reason = accept_performance_level("efficient", current="balanced")
        self.assertEqual((accepted, reason), ("efficient", "capability-or-performance-downgrade"))
        accepted, reason = accept_performance_level("full", current="efficient")
        self.assertEqual((accepted, reason), ("efficient", "upgrade-blocked-downgrade-only"))

    def test_v141_durable_performance_collapses_to_accessible_semantics(self) -> None:
        resolution = resolve_glaze_optics_v141(overrides={"appearance":"light"}, requested_performance_level="durable", current_performance_level="full")
        self.assertEqual(resolution.accepted_performance_level, "durable")
        self.assertEqual(resolution.state.mode, "solid-accessible")
        self.assertEqual(resolution.state.blur_scale, 0.0)
        self.assertEqual(resolution.state.semantic_protection, 1.0)

    def test_v141_engine_metadata_records_current_patch_boundaries(self) -> None:
        self.assertEqual(GLAZE_OPTICAL_ENGINE_V14_1["version"], "1.4.1")
        self.assertEqual(GLAZE_OPTICAL_ENGINE_V14_1["stable_baseline"], "1.4.0")
        self.assertEqual(GLAZE_OPTICAL_ENGINE_V14_1["performance_governance"], "downgrade-only-in-session")
        self.assertFalse(GLAZE_OPTICAL_ENGINE_V14_1["telemetry_required"])
        self.assertFalse(GLAZE_OPTICAL_ENGINE_V14_1["remote_context_required"])

    def test_care_default_adapter_does_not_collect_environment_context(self) -> None:
        state = care_default_optical_state(appearance="dark", reduced_transparency=False, reduced_motion=False)
        self.assertEqual(state.background_complexity, "unknown")
        self.assertEqual(state.background_luminance, "dark")
        self.assertEqual(state.daypart, "unknown")
        self.assertIsNone(state.memory_tint)

    def test_v14_preserves_native_desktop_responsiveness(self) -> None:
        source = _source("glaze_v14.py")
        for state in ("form-factor-compact","form-factor-narrow-desktop","form-factor-desktop","form-factor-wide-desktop"):
            self.assertIn(state, source)
        self.assertIn("MIN_TARGET_PX = 48", source)

    def test_v14_global_controller_is_active_entrypoint(self) -> None:
        main_source = _source("__main__.py")
        self.assertIn("from .glaze_v14_global import install_glaze_v14_global_style", main_source)
        self.assertIn("install_glaze_v14_global_style()", main_source)


if __name__ == "__main__":
    unittest.main()
