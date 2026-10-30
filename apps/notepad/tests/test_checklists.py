"""Checklist edits only target valid Markdown source markers."""
import unittest
from goreecloud_notepad.checklists import task_marker_at_line
from goreecloud_notepad.markdown import parse_markdown


class ChecklistTests(unittest.TestCase):
    def test_check_uncheck_and_uppercase(self):
        self.assertEqual(task_marker_at_line("- [ ] Task", 0), (3, "x"))
        self.assertEqual(task_marker_at_line("- [x] Task", 0), (3, " "))
        self.assertEqual(task_marker_at_line("- [X] Task", 0), (3, " "))

    def test_indented_unicode_and_neighbors(self):
        text = "Title\n  * [ ] Café ☕\n- [x] Done"
        self.assertEqual(task_marker_at_line(text, 1), (5, "x"))
        self.assertEqual(task_marker_at_line(text, 2), (3, " "))
        self.assertIsNone(task_marker_at_line(text, 0))

    def test_fenced_code_not_interactive(self):
        fence = chr(96) * 3
        text = fence + "md\n- [ ] Not a task\n" + fence + "\n- [ ] Real task"
        self.assertIsNone(task_marker_at_line(text, 1))
        self.assertEqual(task_marker_at_line(text, 3), (3, "x"))

    def test_other_markup_and_boundaries(self):
        self.assertIsNone(task_marker_at_line("- bullet", 0))
        self.assertIsNone(task_marker_at_line("- [ ] Task", -1))
        self.assertIsNone(task_marker_at_line("- [ ] Task", 7))
        self.assertIsNone(task_marker_at_line("    - [ ] Too indented", 0))

    def test_preview_source_lines_with_fenced_code(self):
        fence = chr(96) * 3
        lines = parse_markdown(fence + "\n- [ ] Code\n" + fence + "\n- [ ] Live")
        self.assertEqual(lines[-1].source_line, 3)
        self.assertEqual(lines[-1].runs[0].style, "task")
        self.assertIsNone(task_marker_at_line("- [ ] Live", 1))


if __name__ == "__main__":
    unittest.main()
