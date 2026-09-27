import os
import unittest
from unittest.mock import patch

from goreecloud_care.ui_contract import (
    COMPACT_WIDTH,
    MIN_WINDOW_HEIGHT,
    MIN_WINDOW_WIDTH,
    effective_layout_width,
    is_compact_width,
    is_high_contrast_theme,
    text_scale_from_environment,
)


class UIContractTests(unittest.TestCase):
    def test_compact_breakpoint_is_deterministic_at_normal_text(self):
        self.assertTrue(is_compact_width(COMPACT_WIDTH - 1, text_scale=1.0))
        self.assertFalse(is_compact_width(COMPACT_WIDTH, text_scale=1.0))
        self.assertFalse(is_compact_width(COMPACT_WIDTH + 1, text_scale=1.0))

    def test_compact_breakpoint_covers_normal_text_narrow_range(self):
        self.assertTrue(is_compact_width(800, text_scale=1.0))
        self.assertFalse(is_compact_width(900, text_scale=1.0))

    def test_200_percent_text_uses_effective_layout_width(self):
        self.assertEqual(effective_layout_width(900, text_scale=2.0), 450.0)
        self.assertTrue(is_compact_width(900, text_scale=2.0))
        self.assertTrue(is_compact_width(1600, text_scale=2.0))
        self.assertFalse(is_compact_width(COMPACT_WIDTH * 2, text_scale=2.0))

    def test_gdk_dpi_scale_drives_default_large_text_compact_decision(self):
        with patch.dict(os.environ, {"GDK_DPI_SCALE": "2"}, clear=False):
            self.assertEqual(text_scale_from_environment(), 2.0)
            self.assertTrue(is_compact_width(900))

    def test_missing_gdk_dpi_scale_uses_baseline(self):
        with patch.dict(os.environ, {}, clear=True):
            self.assertEqual(text_scale_from_environment(), 1.0)
            self.assertFalse(is_compact_width(900))

    def test_invalid_or_subnormal_text_scale_falls_back_to_baseline(self):
        for value in ("", "invalid", "0", "-1", "nan", "inf", "0.5"):
            with self.subTest(value=value):
                self.assertEqual(text_scale_from_environment(value), 1.0)

    def test_minimum_window_remains_usable_desktop_size(self):
        self.assertGreaterEqual(MIN_WINDOW_WIDTH, 480)
        self.assertGreaterEqual(MIN_WINDOW_HEIGHT, 420)

    def test_high_contrast_theme_variants_are_recognized(self):
        for name in (
            "HighContrast",
            "HighContrastInverse",
            "high-contrast",
            "high_contrast",
            "High Contrast",
        ):
            with self.subTest(name=name):
                self.assertTrue(is_high_contrast_theme(name, gtk_theme_override=""))

    def test_gtk_theme_override_is_part_of_effective_high_contrast_state(self):
        for override in ("HighContrast", "HighContrast:dark", "high-contrast"):
            with self.subTest(override=override):
                self.assertTrue(
                    is_high_contrast_theme(
                        "GoreeCloud-Zorin-Light",
                        gtk_theme_override=override,
                    )
                )

    def test_process_environment_high_contrast_override_is_detected(self):
        with patch.dict(os.environ, {"GTK_THEME": "HighContrast"}, clear=False):
            self.assertTrue(is_high_contrast_theme("GoreeCloud-Zorin-Light"))

    def test_normal_themes_are_not_high_contrast(self):
        for name in (None, "", "ZorinBlue-Light", "Adwaita", "Adwaita-dark"):
            with self.subTest(name=name):
                self.assertFalse(is_high_contrast_theme(name, gtk_theme_override=""))


if __name__ == "__main__":
    unittest.main()
