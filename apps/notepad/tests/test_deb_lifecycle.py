"""Non-privileged dpkg install, simulated upgrade, and removal in a fake root.

Never installs on the host, never uses sudo, and never accesses the host dpkg DB.
Run with python3 tests/test_deb_lifecycle.py after installing dpkg and fakeroot.
"""
from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
BUILDER = APP / "packaging" / "build_deb.py"
PACKAGE = "goreecloud-notepad"


def run(args):
    return subprocess.run(args, check=True, text=True, capture_output=True)


def lifecycle():
    if not shutil.which("fakeroot") or not shutil.which("dpkg-deb"):
        raise RuntimeError("fakeroot and dpkg-deb are required")

    with tempfile.TemporaryDirectory(prefix="gcn-dpkg-lifecycle-") as directory:
        temp = Path(directory)
        package_dir = temp / "packages"
        run([sys.executable, str(BUILDER), "--output", str(package_dir)])
        current = next(package_dir.glob(f"{PACKAGE}_0.1.0_*.deb"))

        # Synthetic old package from the current archive: tests the dpkg
        # upgrade mechanics, not any genuine previously published release.
        older_stage = temp / "old-stage"
        run(["dpkg-deb", "-R", str(current), str(older_stage)])
        control = older_stage / "DEBIAN" / "control"
        metadata = control.read_text(encoding="utf-8")
        if metadata.count("Version: 0.1.0\n") != 1:
            raise AssertionError("Unexpected package version")
        control.write_text(
            metadata.replace("Version: 0.1.0\n", "Version: 0.0.9\n"),
            encoding="utf-8",
        )
        old_package = package_dir / f"{PACKAGE}_0.0.9_all.deb"
        run(["dpkg-deb", "--build", "--root-owner-group", str(older_stage), str(old_package)])

        fake_root = temp / "fake-root"
        admindir = fake_root / "var" / "lib" / "dpkg"
        admindir.mkdir(parents=True)
        (admindir / "status").write_text("", encoding="utf-8")
        saved_note = fake_root / "home" / "test-user" / "Documents" / "safe.md"
        saved_note.parent.mkdir(parents=True)
        original = b"# Saved data\r\n- [ ] Survives upgrade and removal\n"
        saved_note.write_bytes(original)

        def dpkg(*arguments):
            # Force dependencies only because the fake root's dpkg database is
            # empty. Never use this option for an actual user installation.
            run([
                "fakeroot", "dpkg", f"--root={fake_root}",
                f"--log={temp / 'dpkg.log'}",
                "--force-depends", "--no-triggers", *arguments,
            ])

        def status():
            return run([
                "dpkg-query", f"--admindir={admindir}", "-W",
                "-f=$"+"{Status}\t$"+"{Version}\n", PACKAGE,
            ]).stdout.strip()

        installed_launcher = fake_root / "usr" / "bin" / PACKAGE
        installed_module = (
            fake_root / "usr" / "share" / "goreecloud" / "notepad"
            / "goreecloud_notepad" / "storage.py"
        )

        dpkg("-i", str(old_package))
        assert status() == "install ok installed\t0.0.9"
        assert installed_launcher.is_file() and installed_module.is_file()
        assert saved_note.read_bytes() == original

        dpkg("-i", str(current))
        assert status() == "install ok installed\t0.1.0"
        assert installed_launcher.is_file() and installed_module.is_file()
        assert saved_note.read_bytes() == original

        dpkg("-r", PACKAGE)
        try:
            after = status()
        except subprocess.CalledProcessError:
            after = ""
        assert "install ok installed" not in after
        assert not installed_launcher.exists()
        assert not installed_module.exists()
        assert saved_note.read_bytes() == original
        print("Isolated dpkg install / simulated upgrade / remove: PASS")
        print("Unmanaged user note preserved byte-for-byte: PASS")


if __name__ == "__main__":
    lifecycle()
