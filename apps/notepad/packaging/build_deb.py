#!/usr/bin/env python3
"""Build a local first-party Debian package for GoreeCloud Notepad."""
from __future__ import annotations
import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

VERSION = "0.1.0"
ROOT = Path(__file__).resolve().parents[1]
MODULES = ("__init__.py", "__main__.py", "app.py", "checklists.py", "find.py", "markdown.py", "preview.py", "storage.py", "theme.py")

DESKTOP = """[Desktop Entry]
Type=Application
Name=GoreeCloud Notepad
Comment=Quick local notes with Markdown preview
Exec=goreecloud-notepad %F
TryExec=goreecloud-notepad
Icon=accessories-text-editor
Terminal=false
Categories=Utility;TextEditor;GTK;
MimeType=text/plain;text/markdown;
StartupNotify=true
"""
CONTROL = """Package: goreecloud-notepad
Version: {version}
Section: editors
Priority: optional
Architecture: all
Maintainer: GoreeCloud <admin@goreecloud.com>
Depends: python3 (>= 3.10), python3-gi, gir1.2-gtk-4.0
Description: GoreeCloud native GTK4 Notepad (preview)
 Local-first UTF-8 notes, tabs, Markdown preview, and native desktop UI.
 This package does not install a network service or collect analytics.
"""
LAUNCHER = """#!/bin/sh
set -eu
exec /usr/bin/python3 /usr/share/goreecloud/notepad/entrypoint.py "$@"
"""
ENTRYPOINT = """from goreecloud_notepad.app import main

raise SystemExit(main())
"""

def write_file(path: Path, contents: str, mode: int = 0o644) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(contents, encoding="utf-8", newline="\n")
    path.chmod(mode)


def build(output: Path) -> Path:
    os.umask(0o022)
    if shutil.which("dpkg-deb") is None:
        raise RuntimeError("dpkg-deb is required to build a Debian package")
    output = output.expanduser().resolve()
    output.mkdir(parents=True, exist_ok=True)
    package = output / f"goreecloud-notepad_{VERSION}_all.deb"
    with tempfile.TemporaryDirectory(prefix="goreecloud-notepad-deb-") as temp:
        stage = Path(temp) / "package"
        target = stage / "usr/share/goreecloud/notepad/goreecloud_notepad"
        target.mkdir(parents=True)
        for name in MODULES:
            source = ROOT / "goreecloud_notepad" / name
            if not source.is_file() or source.is_symlink():
                raise RuntimeError(f"Missing or unsafe source: {source}")
            shutil.copyfile(source, target / name)
            (target / name).chmod(0o644)
        write_file(stage / "usr/share/goreecloud/notepad/entrypoint.py", ENTRYPOINT)
        write_file(stage / "usr/bin/goreecloud-notepad", LAUNCHER, 0o755)
        desktop = stage / "usr/share/applications/com.goreecloud.Notepad.desktop"
        write_file(desktop, DESKTOP)
        write_file(stage / "DEBIAN/control", CONTROL.format(version=VERSION))
        if shutil.which("desktop-file-validate"):
            subprocess.run(["desktop-file-validate", str(desktop)], check=True)
        subprocess.run(
            ["dpkg-deb", "--build", "--root-owner-group", str(stage), str(package)],
            check=True,
        )
    return package

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=ROOT / "dist",
        help="Output directory; default apps/notepad/dist",
    )
    args = parser.parse_args()
    print(build(args.output))
