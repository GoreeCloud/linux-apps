#!/bin/sh
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
VERSION="0.1.0~dev17"
ARCH="all"
PKG="goreecloud-care"
OUT=${1:-"$ROOT/dist"}
STAGE=$(mktemp -d)
chmod 0755 "$STAGE"
trap 'rm -rf "$STAGE"' EXIT INT TERM
mkdir -p "$OUT" \
  "$STAGE/DEBIAN" \
  "$STAGE/usr/bin" \
  "$STAGE/usr/lib/goreecloud-care/goreecloud_care" \
  "$STAGE/usr/share/applications" \
  "$STAGE/usr/share/metainfo" \
  "$STAGE/usr/share/polkit-1/actions" \
  "$STAGE/usr/share/doc/goreecloud-care"
cat > "$STAGE/DEBIAN/control" <<CONTROL
Package: $PKG
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: GoreeCloud <support@goreecloud.com>
Depends: python3, python3-gi, gir1.2-gtk-3.0, gir1.2-atk-1.0, policykit-1
Homepage: https://goreecloud.com/
Description: GoreeCloud Care Development maintenance utility
 Local-first GTK maintenance utility for Zorin OS and compatible Linux systems.
CONTROL
install -m 0755 "$ROOT/packaging/goreecloud-care" "$STAGE/usr/bin/goreecloud-care"
install -m 0755 "$ROOT/packaging/goreecloud-care-helper" "$STAGE/usr/lib/goreecloud-care/goreecloud-care-helper"
install -m 0644 "$ROOT/goreecloud_care/"*.py "$STAGE/usr/lib/goreecloud-care/goreecloud_care/"
install -m 0644 "$ROOT/packaging/com.goreecloud.care.dev.desktop" "$STAGE/usr/share/applications/"
install -m 0644 "$ROOT/packaging/com.goreecloud.care.dev.metainfo.xml" "$STAGE/usr/share/metainfo/"
install -m 0644 "$ROOT/packaging/com.goreecloud.care.policy" "$STAGE/usr/share/polkit-1/actions/"
install -m 0644 "$ROOT/LICENSE" "$STAGE/usr/share/doc/goreecloud-care/copyright"
cat > "$STAGE/usr/lib/goreecloud-care/goreecloud_care.pth" <<'PTH'
/usr/lib/goreecloud-care
PTH
mkdir -p "$STAGE/usr/lib/python3/dist-packages"
install -m 0644 "$STAGE/usr/lib/goreecloud-care/goreecloud_care.pth" "$STAGE/usr/lib/python3/dist-packages/goreecloud_care.pth"
dpkg-deb --root-owner-group --build "$STAGE" "$OUT/${PKG}_${VERSION}_${ARCH}.deb" >/dev/null
printf '%s\n' "$OUT/${PKG}_${VERSION}_${ARCH}.deb"
