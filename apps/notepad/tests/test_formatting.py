"""Formatting transformations are deterministic, reversible, and local."""
import unittest
from goreecloud_notepad.formatting import MARKERS, heading_prefix_change, inline_format


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


class MarkdownHeadingTests(unittest.TestCase):
    def test_toggle_and_switch_heading_levels_without_rewriting_content(self):
        for level in (1, 2, 3):
            with self.subTest(level=level):
                removed, inserted = heading_prefix_change("GoreeCloud 🚀", level)
                self.assertEqual((removed, inserted), (0, "#" * level + " "))
                line = inserted + "GoreeCloud 🚀"
                removed, inserted = heading_prefix_change(line, level)
                self.assertEqual(line[removed:], "GoreeCloud 🚀")
                self.assertEqual(inserted, "")
        self.assertEqual(heading_prefix_change("## Project", 1), (3, "# "))
        self.assertEqual(heading_prefix_change("###  Title", 2), (5, "## "))
        self.assertEqual(heading_prefix_change("#hashtag", 1), (0, "# "))

    def test_rejects_invalid_heading_requests(self):
        for line, level in (("one\ntwo", 1), ("one\rtwo", 1), ("Heading", 0), ("Heading", 4), ("Heading", True), (None, 1)):
            with self.subTest(line=line, level=level):
                with self.assertRaises(ValueError):
                    heading_prefix_change(line, level)


if __name__ == "__main__":
    unittest.main()
