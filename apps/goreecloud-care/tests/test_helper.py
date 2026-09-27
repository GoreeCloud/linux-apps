import unittest
from unittest import mock

from goreecloud_care import helper


class HelperTests(unittest.TestCase):
    def test_rejects_unknown_action(self):
        self.assertEqual(helper.main(["anything-else"]), 64)

    @mock.patch("goreecloud_care.helper.os.geteuid", return_value=1000)
    def test_requires_root(self, _geteuid):
        self.assertEqual(helper.main(["apt-clean"]), 1)

    @mock.patch("goreecloud_care.helper.os.geteuid", return_value=0)
    @mock.patch("goreecloud_care.helper.subprocess.run")
    def test_apt_clean_uses_static_argv(self, run, _geteuid):
        run.return_value = mock.Mock(returncode=0)
        self.assertEqual(helper.main(["apt-clean"]), 0)
        argv = run.call_args.args[0]
        self.assertEqual(argv, ["/usr/bin/apt-get", "clean"])
        self.assertNotIsInstance(argv, str)


if __name__ == "__main__":
    unittest.main()
