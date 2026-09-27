from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "goreecloud_care"


def _source(name: str) -> str:
    return (PACKAGE / name).read_text(encoding="utf-8")


class GlazeV22ContractTests(unittest.TestCase):
    def test_v22_declares_current_stable_target_and_exact_authority(self) -> None:
        source = _source("glaze_v22.py")
        self.assertIn('GLAZE_UI_TARGET_VERSION = "2.2.0"', source)
        self.assertIn(
            'GLAZE_UI_SOURCE_REVISION = "6731098b28dd0393faa878c70d989a221d714a20"',
            source,
        )
        self.assertIn('GLAZE_UI_RELEASE_TAG = "v2.2.0"', source)
        self.assertIn(
            'GLAZE_UI_APPROVED_VISUAL_SOURCE = "0411b0f6dd877aea30e2c5674e1acde0105fd97b"',
            source,
        )
        self.assertIn('GLAZE_UI_ADOPTION_STATE = "development"', source)
        self.assertIn("GLAZE_UI_CONSUMER_ELIGIBLE = False", source)

    def test_v22_keeps_v14_as_regression_not_active_identity(self) -> None:
        source = _source("glaze_v22.py")
        self.assertIn("CSS as V14_CSS", source)
        self.assertIn('GLAZE_UI_PREVIOUS_CARE_BASELINE = "1.4.0"', source)
        self.assertIn('V14_CSS.replace(b"glaze-v14", b"glaze-v22")', source)
        main_source = _source("__main__.py")
        self.assertNotIn("install_glaze_v14_global_style()", main_source)

    def test_v22_maps_system_shell_and_glaze_budget_explicitly(self) -> None:
        source = _source("glaze_v22.py")
        for role in (
            '"workspace"',
            '"application"',
            '"system-overlay"',
            '"system-panel"',
            '"critical-system"',
        ):
            self.assertIn(role, source)
        self.assertIn('"dominant_panels_max": 1', source)
        self.assertIn('"small_floating_controls_max": 3', source)
        self.assertIn('"nested_backdrop_blur": False', source)
        self.assertIn("solid where users read or make critical decisions", source.lower())

    def test_v22_scopes_native_product_form_factors_truthfully(self) -> None:
        source = _source("glaze_v22.py")
        self.assertIn('SUPPORTED_PRODUCT_FORM_FACTORS = ("desktop", "wide-desktop")', source)
        for unsupported in ("phone", "tablet", "tv", "foldable", "wearable", "spatial"):
            self.assertIn(f'"{unsupported}"', source)
        self.assertIn("native_form_factor_for_window_width", source)
        self.assertIn("layout_environment", source)

    def test_v22_accessibility_precedence_has_native_equivalents(self) -> None:
        source = _source("glaze_v22.py")
        global_source = _source("glaze_v22_global.py")
        self.assertIn("MIN_TARGET_PX = 48", source)
        self.assertIn("TOUCH_ASSISTANCE_TARGET_PX = 56", source)
        self.assertIn('"forced-colors": "GTK HighContrast/system palette authority"', source)
        self.assertIn("touch-assistance", source)
        self.assertIn("increased-contrast", source)
        self.assertIn("effects-reduced", source)
        self.assertIn("is_high_contrast_theme", global_source)

    def test_v22_resolves_safety_state_before_race_free_window_binding(self) -> None:
        global_source = _source("glaze_v22_global.py")
        self.assertIn("def _runtime_css(", global_source)
        self.assertIn('data = data.replace(b"window.glaze-v22", b"window")', global_source)
        self.assertIn("self.provider.load_from_data(runtime_css)", global_source)
        self.assertIn("GLib.idle_add(self._attach_application)", global_source)
        self.assertNotIn("GLib.timeout_add(100, self._attach_application)", global_source)
        self.assertLess(
            global_source.index("self.sync()"),
            global_source.index("GLib.idle_add(self._attach_application)"),
        )

    def test_v22_is_the_active_native_provider(self) -> None:
        main_source = _source("__main__.py")
        self.assertIn("from .glaze_v22_global import install_glaze_v22_global_style", main_source)
        self.assertIn("install_glaze_v22_global_style()", main_source)
        self.assertNotIn("from .glaze_v14_global import", main_source)

    def test_v22_does_not_self_certify_care(self) -> None:
        source = _source("glaze_v22.py")
        self.assertIn("does not certify GoreeCloud Care", source)
        self.assertIn("Development / nonconformant consumer", source)


if __name__ == "__main__":
    unittest.main()
