from __future__ import annotations

from pathlib import Path
import unittest

from goreecloud_care.glaze_v15 import (
    GLAZE_UI_ADOPTION_STATE,
    GLAZE_UI_CONSUMER_ELIGIBLE,
    GLAZE_UI_LABEL,
    GLAZE_UI_REVIEWED_IMPLEMENTATION_ANCHOR,
    GLAZE_UI_SOURCE_REVISION,
    GLAZE_UI_STABLE_BASELINE,
    GLAZE_UI_TARGET_VERSION,
    CapabilityFact,
    PresentationContext,
    privileged_maintenance_capability,
    resolve_capability_facts,
    resolve_presentation,
)

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "goreecloud_care"


class GlazeV15ContractTests(unittest.TestCase):
    def test_v15_declares_current_stable_target_without_claiming_acceptance(self) -> None:
        self.assertEqual(GLAZE_UI_LABEL, "GLAZE UI V1.5 — Contextual + Capability Awareness")
        self.assertEqual(GLAZE_UI_TARGET_VERSION, "1.5.0")
        self.assertEqual(GLAZE_UI_STABLE_BASELINE, "1.4.1")
        self.assertEqual(GLAZE_UI_ADOPTION_STATE, "development")
        self.assertFalse(GLAZE_UI_CONSUMER_ELIGIBLE)
        self.assertEqual(GLAZE_UI_SOURCE_REVISION, "b7fa8164bfdeaa1dc0acb21b770e7601120da04e")
        self.assertEqual(
            GLAZE_UI_REVIEWED_IMPLEMENTATION_ANCHOR,
            "ee1032a0822ab8e103f8afe48e5c1859fde65cc9",
        )

    def test_v15_is_additive_to_retained_v141_optical_baseline(self) -> None:
        source = (PACKAGE / "glaze_v15.py").read_text(encoding="utf-8")
        self.assertIn("from .glaze_v14 import layout_environment", source)
        self.assertIn('GLAZE_UI_STABLE_BASELINE = "1.4.1"', source)

    def test_conflicting_provider_truth_fails_closed(self) -> None:
        resolved = resolve_capability_facts(
            [
                CapabilityFact("cleanup", "provider-a", "available", "ready", "a"),
                CapabilityFact("cleanup", "provider-b", "unavailable", "blocked", "b"),
            ]
        )
        self.assertEqual(resolved.state, "unknown")
        self.assertEqual(resolved.provider, "conflict")
        self.assertIn("failed closed", resolved.reason)

    def test_agreeing_providers_do_not_expand_authority(self) -> None:
        resolved = resolve_capability_facts(
            [
                CapabilityFact("cleanup", "provider-a", "degraded", "limited", "a"),
                CapabilityFact("cleanup", "provider-b", "degraded", "limited", "b"),
            ]
        )
        presentation = resolve_presentation(resolved)
        self.assertEqual(presentation.state, "degraded")
        self.assertTrue(presentation.enabled)
        self.assertFalse(presentation.automatic_execution_allowed)
        self.assertFalse(presentation.automatic_fallback_allowed)

    def test_unavailable_capability_is_disabled_and_explained(self) -> None:
        fact = CapabilityFact(
            "privileged-maintenance",
            "goreecloud-care",
            "unavailable",
            "helper unavailable",
            "local-check",
        )
        presentation = resolve_presentation(fact)
        self.assertFalse(presentation.enabled)
        self.assertIn("Unavailable", presentation.explanation)
        self.assertIn("capability-unavailable", presentation.css_classes)

    def test_accessibility_precedence_is_explicit_in_presentation_classes(self) -> None:
        presentation = resolve_presentation(
            CapabilityFact("cleanup", "care", "available", "ready", "local"),
            PresentationContext(
                runtime_pressure="critical",
                reduced_motion=True,
                reduced_transparency=True,
                increased_contrast=True,
            ),
        )
        self.assertIn("accessibility-priority", presentation.css_classes)
        self.assertIn("accessibility-reduced-motion", presentation.css_classes)
        self.assertIn("accessibility-reduced-transparency", presentation.css_classes)
        self.assertIn("accessibility-increased-contrast", presentation.css_classes)
        self.assertTrue(presentation.enabled)

    def test_malformed_runtime_context_degrades_presentation_without_gaining_authority(self) -> None:
        presentation = resolve_presentation(
            CapabilityFact("cleanup", "care", "available", "ready", "local"),
            PresentationContext(runtime_pressure="impossible", connectivity="invalid"),
        )
        self.assertIn("runtime-pressure-critical", presentation.css_classes)
        self.assertIn("connectivity-unknown", presentation.css_classes)
        self.assertFalse(presentation.automatic_execution_allowed)

    def test_privileged_capability_requires_helper_and_pkexec(self) -> None:
        no_helper = privileged_maintenance_capability(
            helper_executable=False,
            pkexec_available=True,
        )
        self.assertEqual(no_helper.state, "unavailable")
        self.assertIn("helper", no_helper.reason.lower())

        no_pkexec = privileged_maintenance_capability(
            helper_executable=True,
            pkexec_available=False,
        )
        self.assertEqual(no_pkexec.state, "unavailable")
        self.assertIn("pkexec", no_pkexec.reason.lower())

        available = privileged_maintenance_capability(
            helper_executable=True,
            pkexec_available=True,
        )
        self.assertEqual(available.state, "available")
        self.assertIn("request administrator authorization", available.reason)

    def test_presentation_never_requests_or_grants_permission(self) -> None:
        source = (PACKAGE / "glaze_v15.py").read_text(encoding="utf-8")
        self.assertNotIn("subprocess", source)
        self.assertNotIn("pkexec(", source)
        self.assertIn("never grants authority", source)
        self.assertIn("automatic_execution_allowed=False", source)
        self.assertIn("automatic_fallback_allowed=False", source)


if __name__ == "__main__":
    unittest.main()
