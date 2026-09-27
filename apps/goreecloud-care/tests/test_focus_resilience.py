import unittest

from goreecloud_care.focus_resilience import FOCUS_RESILIENCE_CSS


class FocusResilienceTests(unittest.TestCase):
    def setUp(self):
        self.css = FOCUS_RESILIENCE_CSS.decode("utf-8")

    def test_focus_fallback_covers_buttons(self):
        self.assertIn("button:focus", self.css)

    def test_focus_fallback_covers_checkbuttons(self):
        self.assertIn("checkbutton:focus", self.css)

    def test_focus_fallback_uses_theme_derived_color(self):
        self.assertIn("@theme_fg_color", self.css)

    def test_focus_fallback_does_not_define_application_palette(self):
        for property_name in ("background:", "background-color:", "color: #"):
            with self.subTest(property_name=property_name):
                self.assertNotIn(property_name, self.css)


if __name__ == "__main__":
    unittest.main()
