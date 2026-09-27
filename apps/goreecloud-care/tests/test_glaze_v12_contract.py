from __future__ import annotations

import unittest
from unittest.mock import patch

from goreecloud_care.glaze_v12 import (
    APPEARANCE_ENV,
    CSS,
    GLAZE_UI_LABEL,
    GLAZE_UI_VERSION,
    MIN_TARGET_PX,
    REDUCE_MOTION_ENV,
    REDUCE_TRANSPARENCY_ENV,
    appearance_from_theme,
    reduced_motion_requested,
    reduced_transparency_requested,
)
from goreecloud_care.glaze_v12_global import _runtime_css


class GlazeV12ContractTests(unittest.TestCase):
    def test_current_stable_identity_is_v12(self) -> None:
        self.assertEqual(GLAZE_UI_LABEL, "GLAZE UI V1.2")
        self.assertEqual(GLAZE_UI_VERSION, "1.2.0")
        self.assertEqual(MIN_TARGET_PX, 48)

    def test_system_light_and_dark_are_resolved_without_forcing_palette(self) -> None:
        self.assertEqual(
            appearance_from_theme("ZorinBlue-Light", appearance_override="system", gtk_theme_override=""),
            "light",
        )
        self.assertEqual(
            appearance_from_theme("Adwaita-dark", appearance_override="system", gtk_theme_override=""),
            "dark",
        )

    def test_explicit_deep_dark_override_is_bounded(self) -> None:
        with patch.dict("os.environ", {APPEARANCE_ENV: "deep-dark"}, clear=False):
            self.assertEqual(appearance_from_theme("Adwaita"), "deep-dark")

    def test_reduced_transparency_is_explicit_and_fail_safe(self) -> None:
        for value in ("1", "true", "yes", "on"):
            with self.subTest(value=value):
                self.assertTrue(reduced_transparency_requested(value))
        for value in (None, "", "0", "false", "off"):
            with self.subTest(value=value):
                with patch.dict("os.environ", {}, clear=True):
                    self.assertFalse(reduced_transparency_requested(value))

    def test_reduced_motion_honors_gtk_animation_disable_or_explicit_request(self) -> None:
        self.assertTrue(reduced_motion_requested(False, value="0"))
        self.assertFalse(reduced_motion_requested(True, value="0"))
        self.assertTrue(reduced_motion_requested(True, value="1"))

    def test_material_is_neutral_and_accent_is_semantic(self) -> None:
        text = CSS.decode("utf-8")
        self.assertIn("rgba(255, 255, 255, 0.72)", text)
        self.assertIn("background: #2f6fed", text)
        self.assertIn("button, checkbutton { min-height: 48px; }", text)
        self.assertIn("reduced-transparency", text)
        self.assertIn("reduced-motion", text)
        self.assertNotIn("transition:", text)
        self.assertNotIn("animation:", text)

    def test_runtime_css_promotes_only_the_resolved_state(self) -> None:
        light = _runtime_css("light", reduced_transparency=False, reduced_motion=False).decode()
        dark = _runtime_css("dark", reduced_transparency=False, reduced_motion=False).decode()
        solid = _runtime_css("light", reduced_transparency=True, reduced_motion=True).decode()
        self.assertIn("window {\n  background: #edf0f4", light)
        self.assertIn("window {\n  background: #18191b", dark)
        self.assertIn("window headerbar,\nwindow .card { background: #ffffff; }", solid)

    def test_environment_names_are_product_scoped(self) -> None:
        self.assertTrue(APPEARANCE_ENV.startswith("GOREECLOUD_CARE_"))
        self.assertTrue(REDUCE_TRANSPARENCY_ENV.startswith("GOREECLOUD_CARE_"))
        self.assertTrue(REDUCE_MOTION_ENV.startswith("GOREECLOUD_CARE_"))


if __name__ == "__main__":
    unittest.main()
