"""Deterministic, source-preserving Markdown decoration offsets."""
import unittest

from goreecloud_notepad.source_spans import MAX_STYLED_CHARS, Span, source_spans


class SourceSpansTests(unittest.TestCase):
    def test_heading_and_embedded_bold(self):
        spans = source_spans("# H **bold**\n")
        self.assertIn(Span(0, 1, "marker"), spans)
        self.assertIn(Span(2, 12, "h1"), spans)
        self.assertIn(Span(6, 10, "bold"), spans)
        self.assertIn(Span(4, 6, "marker"), spans)
        self.assertIn(Span(10, 12, "marker"), spans)

    def test_unicode_offsets(self):
        text = "🌟 **café**"
        spans = source_spans(text)
        self.assertIn(Span(4, 8, "bold"), spans)
        self.assertEqual(text[4:8], "café")

    def test_fenced_code_is_not_inline_formatted(self):
        fence = chr(96) * 3
        text = fence + "python\n**literal**\n" + fence + "\n**styled**"
        spans = source_spans(text)
        self.assertEqual(len([s for s in spans if s.style == "bold"]), 1)
        self.assertIn(Span(text.index("literal") - 2,
                           text.index("literal") + len("literal") + 2, "code"), spans)

    def test_checkboxes_and_links(self):
        text = "- [x] Done\nRead [docs](https://example.invalid)"
        spans = source_spans(text)
        self.assertIn(Span(2, 5, "task"), spans)
        self.assertTrue(any(s.style == "link" and text[s.start:s.end] == "docs"
                            for s in spans))
        self.assertTrue(any(s.style == "marker" and "https://" in text[s.start:s.end]
                            for s in spans))

    def test_windows_newlines_do_not_shift_spans(self):
        text = "first\r\n**next**"
        spans = source_spans(text)
        self.assertTrue(any(s.style == "bold" and text[s.start:s.end] == "next"
                            for s in spans))

    def test_html_is_left_literal(self):
        self.assertEqual(source_spans("<script>alert(1)</script>"), [])

    def test_dense_markup_stays_plain_for_performance(self):
        self.assertEqual(source_spans(("*x* " * 2_000).rstrip()), [])

    def test_large_notes_stay_plain_and_fully_editable(self):
        self.assertEqual(source_spans("x" * (MAX_STYLED_CHARS + 1)), [])
        self.assertEqual(source_spans(""), [])


if __name__ == "__main__":
    unittest.main()
