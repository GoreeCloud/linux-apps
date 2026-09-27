import unittest

from goreecloud_care.privilege import interpret_pkexec_result


class PrivilegeOutcomeTests(unittest.TestCase):
    def test_success_is_explicit(self):
        outcome = interpret_pkexec_result(0, "", "APT cache cleanup")
        self.assertTrue(outcome.completed)
        self.assertFalse(outcome.cancelled)
        self.assertIn("completed successfully", outcome.message)

    def test_pkexec_dismissal_is_explicit_and_non_success(self):
        outcome = interpret_pkexec_result(126, "", "APT cache cleanup")
        self.assertFalse(outcome.completed)
        self.assertTrue(outcome.cancelled)
        self.assertIn("was cancelled", outcome.message)
        self.assertIn("made no privileged changes", outcome.message)

    def test_zorin_request_dismissed_text_is_cancelled(self):
        outcome = interpret_pkexec_result(
            1,
            "Error executing command as another user: Request dismissed",
            "APT cache cleanup",
        )
        self.assertFalse(outcome.completed)
        self.assertTrue(outcome.cancelled)
        self.assertIn("was cancelled", outcome.message)
        self.assertIn("made no privileged changes", outcome.message)

    def test_authorization_error_is_not_success(self):
        outcome = interpret_pkexec_result(127, "Not authorized", "Memory-cache reclaim")
        self.assertFalse(outcome.completed)
        self.assertFalse(outcome.cancelled)
        self.assertIn("authorization was not obtained", outcome.message)
        self.assertIn("Not authorized", outcome.message)

    def test_helper_failure_is_not_success(self):
        outcome = interpret_pkexec_result(2, "helper failed", "APT cache cleanup")
        self.assertFalse(outcome.completed)
        self.assertFalse(outcome.cancelled)
        self.assertIn("exit status 2", outcome.message)
        self.assertIn("helper failed", outcome.message)


if __name__ == "__main__":
    unittest.main()
