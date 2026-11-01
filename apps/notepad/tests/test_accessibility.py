"""Pure tests for consistent, non-stateful task accessible names."""
import unittest
from goreecloud_notepad.accessibility import task_accessible_name, MAX_TASK_LABEL


class TaskAccessibilityTests(unittest.TestCase):
    def test_label_describes_original_source_line(self):
        self.assertEqual(task_accessible_name(0, "Write tests"), "Task, line 1: Write tests")
        self.assertEqual(task_accessible_name(12, "  Fix   issue\t123  "), "Task, line 13: Fix issue 123")

    def test_unicode_whitespace_and_empty_text(self):
        self.assertEqual(task_accessible_name(3, "  \u2028 "), "Task, line 4: Empty task")
        self.assertEqual(task_accessible_name(1, "Read \u00e9 and \u2601"), "Task, line 2: Read \u00e9 and \u2601")

    def test_long_text_is_bounded_without_changing_source(self):
        original = "A" * 1000
        actual = task_accessible_name(4, original)
        self.assertEqual(actual, "Task, line 5: " + ("A" * (MAX_TASK_LABEL - 1)) + "\u2026")
        self.assertEqual(original, "A" * 1000)

    def test_negative_line_rejected(self):
        with self.assertRaises(ValueError):
            task_accessible_name(-1, "Never valid")


if __name__ == "__main__":
    unittest.main()
