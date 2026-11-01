"""Fast GTK word-wrap guardrails for pathological source tokens."""
import unittest
from goreecloud_notepad.wrap_policy import FAST_WRAP_RUN, needs_fast_wrap


class WrapPolicyTests(unittest.TestCase):
    def test_regular_prose_remains_word_wrapped(self):
        self.assertFalse(needs_fast_wrap("A short note with multiple words.\n- [ ] Test"))
        self.assertFalse(needs_fast_wrap(("short " * 1000).rstrip()))

    def test_long_unbroken_token_activates_fast_wrap(self):
        self.assertFalse(needs_fast_wrap("x" * (FAST_WRAP_RUN - 1)))
        self.assertTrue(needs_fast_wrap("x" * FAST_WRAP_RUN))
        self.assertTrue(needs_fast_wrap("word " + "x" * FAST_WRAP_RUN + " end"))

    def test_unicode_and_line_breaks_restart_length(self):
        self.assertFalse(needs_fast_wrap(("🌿" * 2000) + "\u2029" + ("🌿" * 2000)))
        self.assertFalse(needs_fast_wrap(("x" * 2000) + "\r\n" + ("x" * 2000)))
        self.assertTrue(needs_fast_wrap("🧡" * FAST_WRAP_RUN))

    def test_invalid_threshold(self):
        with self.assertRaises(ValueError):
            needs_fast_wrap("hello", threshold=0)


if __name__ == "__main__":
    unittest.main()
