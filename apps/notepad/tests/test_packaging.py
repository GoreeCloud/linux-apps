"""Isolated .deb contents and dependency smoke checks."""
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

APP = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("dpkg-deb"), "Debian tooling unavailable")
class DebianPackageTests(unittest.TestCase):
    def test_archive_manifest_and_launcher(self):
        with tempfile.TemporaryDirectory(prefix="notepad-deb-test-") as folder:
            root = Path(folder)
            subprocess.run(
                [sys.executable, str(APP / "packaging/build_deb.py"),
                 "--output", str(root / "out")], check=True, capture_output=True,
            )
            archive = root / "out/goreecloud-notepad_0.1.0_all.deb"
            self.assertTrue(archive.is_file())
            fields = subprocess.check_output(
                ["dpkg-deb", "-f", str(archive), "Package", "Architecture",
                 "Version", "Depends"], text=True,
            )
            self.assertIn("goreecloud-notepad", fields)
            self.assertIn("python3-gi", fields)
            self.assertIn("gir1.2-gtk-4.0", fields)
            subprocess.run(
                ["dpkg-deb", "-x", str(archive), str(root / "extract")],
                check=True, capture_output=True,
            )
            stage = root / "extract/usr"
            launcher = stage / "bin/goreecloud-notepad"
            self.assertTrue(launcher.is_file())
            self.assertTrue(launcher.stat().st_mode & stat.S_IXUSR)
            self.assertIn("/usr/bin/python3", launcher.read_text())
            desktop = stage / "share/applications/com.goreecloud.Notepad.desktop"
            self.assertIn("Exec=goreecloud-notepad %F", desktop.read_text())
            package = stage / "share/goreecloud/notepad/goreecloud_notepad"
            expected = {
                "__init__.py", "__main__.py", "app.py", "checklists.py",
                "find.py", "formatting.py", "markdown.py", "preview.py", "source_spans.py", "source_styling.py", "storage.py", "theme.py",
            }
            self.assertEqual({p.name for p in package.iterdir()}, expected)
            self.assertTrue(all(not p.is_symlink() for p in package.iterdir()))
            self.assertTrue(all((p.stat().st_mode & 0o022) == 0
                                for p in package.iterdir()))


if __name__ == "__main__":
    unittest.main()
