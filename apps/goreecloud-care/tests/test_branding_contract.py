from __future__ import annotations

import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ICON = ROOT / "packaging" / "icons" / "com.goreecloud.care.svg"
CANONICAL_INITIAL_SHA256 = "7ac99c85b16b5633b0ef28f2b8c58966d7eb26ef87118b8ef50121a2c6235d56"
CANONICAL_INITIAL_GIT_BLOB = "c4568ce4b24b9eb47971ec522317b737f1a509c8"


class BrandingContractTests(unittest.TestCase):
    def test_packaged_icon_matches_canonical_dev18_checkpoint(self) -> None:
        data = ICON.read_bytes()
        self.assertEqual(hashlib.sha256(data).hexdigest(), CANONICAL_INITIAL_SHA256)
        branding = (ROOT / "BRANDING.md").read_text(encoding="utf-8")
        self.assertIn("GoreeCloud/goreecloud-branding-assets/products/care/app-icon.svg", branding)
        self.assertIn(CANONICAL_INITIAL_GIT_BLOB, branding)

    def test_desktop_and_appstream_use_care_identity(self) -> None:
        desktop = (ROOT / "packaging" / "com.goreecloud.care.desktop").read_text(encoding="utf-8")
        metainfo = (ROOT / "packaging" / "com.goreecloud.care.metainfo.xml").read_text(encoding="utf-8")
        self.assertIn("Icon=com.goreecloud.care", desktop)
        self.assertIn("Name=GoreeCloud Care", desktop)
        self.assertIn('<icon type="stock">com.goreecloud.care</icon>', metainfo)
        self.assertIn("<name>GoreeCloud Care</name>", metainfo)

    def test_debian_package_installs_icon_to_freedesktop_location(self) -> None:
        build = (ROOT / "scripts" / "build-deb.sh").read_text(encoding="utf-8")
        self.assertIn("/usr/share/icons/hicolor/scalable/apps", build)
        self.assertIn("com.goreecloud.care.svg", build)


if __name__ == "__main__":
    unittest.main()
