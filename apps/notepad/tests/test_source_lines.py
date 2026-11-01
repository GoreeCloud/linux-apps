"""Tests for the source line splitter."""
import unittest
from goreecloud_notepad.source_lines import gtk_source_lines
from goreecloud_notepad.checklists import task_marker_at_line

class LineTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(gtk_source_lines("a\nb"), ["a", "b"])

    def test_line_endings(self):
        for ending in ("\n", "\r", "\r\n", chr(8233)):
            with self.subTest(ending=repr(ending)):
                text = "a" + ending + "- [ ] Task" + ending
                self.assertEqual(gtk_source_lines(text), ["a", "- [ ] Task"])
                self.assertEqual(gtk_source_lines(text, keepends=True), ["a" + ending, "- [ ] Task" + ending])
                self.assertEqual(task_marker_at_line(text, 1), (3, "x"))

    def test_non_gtk_breaks(self):
        for code in (11, 12, 28, 29, 30, 133, 8232):
            text = "Heading" + chr(code) + "- [ ] Ghost\n- [ ] Actual"
            with self.subTest(code=code):
                self.assertEqual(gtk_source_lines(text), ["Heading" + chr(code) + "- [ ] Ghost", "- [ ] Actual"])
                self.assertIsNone(task_marker_at_line(text, 0))
                self.assertEqual(task_marker_at_line(text, 1), (3, "x"))

    def test_parsing_and_source_offsets(self):
        from goreecloud_notepad.markdown import parse_markdown
        from goreecloud_notepad.source_spans import source_spans
        for ending in ('\r\n', chr(8233)):
            raw = 'Heading' + ending + '- [ ] Task'
            parsed = parse_markdown(raw)
            self.assertEqual(parsed[-1].source_line, 1)
            self.assertEqual(parsed[-1].runs[0].style, 'task')
            task_at = len('Heading') + len(ending) + 3
            self.assertTrue(any(span.style == 'task' and span.start <= task_at < span.end for span in source_spans(raw)))
            self.assertEqual(''.join(gtk_source_lines(raw, keepends=True)), raw)
