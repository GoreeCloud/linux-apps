"""Formatting transformations are deterministic, reversible, and local."""
import unittest
from goreecloud_notepad.formatting import MARKERS, inline_format


class MarkdownFormattingTests(unittest.TestCase):
    def _apply(self, text, change):
        return text[:change.start] + change.replacement + text[change.end:]

    def test_selection_wrapping_and_unwrapping(self):
        for style, marker in MARKERS.items():
            with self.subTest(style=style):
                value = "alpha beta gamma"
                change = inline_format(value, 6, 10, style)
                wrapped = self._apply(value, change)
                self.assertEqual(wrapped, "alpha " + marker + "beta" + marker + " gamma")
                self.assertEqual(wrapped[change.selection_start:change.selection_end], "beta")
                undo_format = inline_format(wrapped, change.selection_start, change.selection_end, style)
                self.assertEqual(self._apply(wrapped, undo_format), value)

    def test_wrapped_selection_including_markers(self):
        result = inline_format("**word**", 0, 8, "bold")
        self.assertEqual(self._apply("**word**", result), "word")
        self.assertEqual((result.selection_start, result.selection_end), (0, 4))

    def test_empty_selection_places_cursor_between_markers(self):
        for style, marker in MARKERS.items():
            with self.subTest(style=style):
                result = inline_format("hello", 2, 2, style)
                self.assertEqual(self._apply("hello", result), "he" + marker * 2 + "llo")
                self.assertEqual(result.selection_start, 2 + len(marker))
                self.assertEqual(result.selection_start, result.selection_end)

    def test_multiline_is_intentionally_not_changed(self):
        self.assertIsNone(inline_format("a\nb", 0, 3, "bold"))

    def test_rejects_invalid_inputs(self):
        for values in ((-1, 2), (4, 3), (0, 100)):
            with self.subTest(values=values):
                with self.assertRaises(ValueError):
                    inline_format("hello", *values, "italic")
        with self.assertRaises(ValueError):
            inline_format("test", 0, 4, "unknown")

    def test_unicode_offsets(self):
        value = "🌟 café ☕"
        changed = inline_format(value, 2, 6, "bold")
        self.assertEqual(self._apply(value, changed), "🌟 **café** ☕")
        self.assertEqual(self._apply("🌟 **café** ☕", inline_format(
            "🌟 **café** ☕", changed.selection_start, changed.selection_end, "bold"
        )), value)


if __name__ == "__main__":
    unittest.main()
