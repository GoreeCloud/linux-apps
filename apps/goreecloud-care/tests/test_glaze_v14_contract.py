from __future__ import annotations

from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
PACKAGE = ROOT / "goreecloud_care"


def _source(name: str) -> str:
    return (PACKAGE / name).read_text(encoding="utf-8")


class GlazeV14HistoricalContractTests(unittest.TestCase):
    def test_v14_preserves_exact_historical_target_and_source_revision(self) -> None:
        source = _source("glaze_v14.py")
        self.assertIn('GLAZE_UI_TARGET_VERSION = "1.4.0"', source)
        self.assertIn(
            'GLAZE_UI_SOURCE_REVISION = "01c86323f8b747373d308026adc8b0881855cdc5"',
            source,
        )
        self.assertIn('GLAZE_UI_ADOPTION_STATE = "development"', source)
        self.assertIn("GLAZE_UI_CONSUMER_ELIGIBLE = False", source)

    def test_v14_builds_on_v13_expressive_foundation(self) -> None:
        source = _source("glaze_v14.py")
        self.assertIn("CSS as V13_CSS", source)
        self.assertIn('CSS = V13_CSS + b"\\n" + V14_CSS', source)
        self.assertIn("Functional glass is restricted to command chrome", source)

    def test_v14_preserves_native_desktop_form_factor_regression_states(self) -> None:
        source = _source("glaze_v14.py")
        for state in (
            "form-factor-compact",
            "form-factor-narrow-desktop",
            "form-factor-desktop",
            "form-factor-wide-desktop",
        ):
            self.assertIn(state, source)
        self.assertIn("FORM_FACTOR_NARROW_DESKTOP_MAX = 1023", source)
        self.assertIn("FORM_FACTOR_DESKTOP_MAX = 1199", source)

    def test_v14_preserves_dpi_aware_native_window_classification(self) -> None:
        source = _source("glaze_v14.py")
        global_source = _source("glaze_v14_global.py")
        self.assertIn("effective_layout_width", source)
        self.assertIn("is_compact_width", source)
        self.assertIn("native_form_factor_for_window_width", source)
        self.assertIn("native_form_factor_for_window_width", global_source)

    def test_v14_preserves_safety_state_regression_contract(self) -> None:
        global_source = _source("glaze_v14_global.py")
        self.assertIn("def _runtime_css(", global_source)
        self.assertIn('data = data.replace(b"window.glaze-v14", b"window")', global_source)
        self.assertIn("self.provider.load_from_data(runtime_css)", global_source)
        self.assertLess(
            global_source.index("self.sync()"),
            global_source.index("GLib.timeout_add(100, self._attach_application)"),
        )

    def test_v14_preserves_accessibility_regression_contract(self) -> None:
        source = _source("glaze_v14.py")
        self.assertIn("reduced-transparency", source)
        self.assertIn("reduced-motion", source)
        self.assertIn("show-borders", source)
        self.assertIn("outline-width: 3px", source)
        self.assertIn("MIN_TARGET_PX = 48", source)

    def test_v14_global_controller_is_not_the_active_entrypoint(self) -> None:
        main_source = _source("__main__.py")
        self.assertNotIn("from .glaze_v14_global import", main_source)
        self.assertNotIn("install_glaze_v14_global_style()", main_source)
        self.assertIn("from .glaze_v22_global import install_glaze_v22_global_style", main_source)
        self.assertIn("install_glaze_v22_global_style()", main_source)

    def test_v14_does_not_claim_downstream_acceptance(self) -> None:
        source = _source("glaze_v14.py")
        self.assertIn("Downstream applications are not certified", source)
        self.assertIn("application-specific validation is accepted", source)


if __name__ == "__main__":
    unittest.main()
