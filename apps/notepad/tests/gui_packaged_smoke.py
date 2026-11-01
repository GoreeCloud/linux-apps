"""Validate extracted Debian GUI payload in a private staging root (no system install)."""
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
PACKAGE_BUILDER = HERE / "packaging" / "build_deb.py"

def main():
    with tempfile.TemporaryDirectory(prefix="gcn-package-audit-") as temporary:
        root = Path(temporary)
        out = root / "dist"
        subprocess.run([sys.executable, str(PACKAGE_BUILDER), "--output", str(out)], check=True, capture_output=True, text=True)
        archive = next(out.glob("goreecloud-notepad_*.deb"))
        staging = root / "stage"
        subprocess.run(["dpkg-deb", "-x", str(archive), str(staging)], check=True)
        payload = staging / "usr/share/goreecloud/notepad"
        entry = payload / "entrypoint.py"
        desktop = staging / "usr/share/applications/com.goreecloud.Notepad.desktop"
        launcher = staging / "usr/bin/goreecloud-notepad"
        assert entry.is_file() and desktop.is_file() and launcher.is_file()
        subprocess.run(["desktop-file-validate", str(desktop)], check=True, capture_output=True, text=True)
        assert launcher.stat().st_mode & 0o111
        assert "Exec=goreecloud-notepad %F" in desktop.read_text()
        private_profile = root / "profile"
        document = root / "notes" / "packaged-test.md"
        document.parent.mkdir()
        # Run from outside the source checkout. Confirm the runtime imported is
        # the extracted package and that a real GTK4 document round-trip works.
        child = """
import os
from pathlib import Path
from gi.repository import Gio
from goreecloud_notepad.app import NotepadApplication
from goreecloud_notepad.storage import Note
import goreecloud_notepad
payload = Path(os.environ["GCN_PAYLOAD"]).resolve()
assert Path(goreecloud_notepad.__file__).resolve().is_relative_to(payload)
app = NotepadApplication()
app.set_flags(Gio.ApplicationFlags.HANDLES_OPEN | Gio.ApplicationFlags.NON_UNIQUE)
app.register()
app.activate()
page = app.window.current()
text = "# Packaged GUI note\\n\\n- [ ] Offline test\\n"
page.buffer.set_text(text)
path = Path(os.environ["GCN_TEST_NOTE"])
page.note.save(path)
assert Note.open(path).text == text
assert page.buffer.get_text(*page.buffer.get_bounds(), True) == text
# Test that the actual packaged application can open a passed file.
app.open([Gio.File.new_for_path(str(path))], "")
assert any(tab.note.path == path and tab.note.text == text
           for tab in app.window.pages)
app.window._close_confirmed = True
app.window.close()
app.quit()
print("Installed-payload GTK4 smoke: PASS")
"""
        env = os.environ.copy()
        env.update(
            PYTHONPATH=str(payload),
            PYTHONDONTWRITEBYTECODE="1",
            XDG_CONFIG_HOME=str(private_profile),
            GCN_PAYLOAD=str(payload),
            GCN_TEST_NOTE=str(document),
        )
        result = subprocess.run(
            ["/usr/bin/python3", "-c", child],
            cwd=str(root),
            env=env,
            capture_output=True,
            text=True,
            timeout=20,
        )
        assert result.returncode == 0, result.stderr
        assert document.read_text() == "# Packaged GUI note\n\n- [ ] Offline test\n"
        # A staged removal must not delete independent user data.
        shutil.rmtree(staging)
        assert document.read_text() == "# Packaged GUI note\n\n- [ ] Offline test\n"
        print(result.stdout.strip())
        print("Debian staged extraction, desktop entry, and profile isolation: PASS")

if __name__ == "__main__":
    main()
