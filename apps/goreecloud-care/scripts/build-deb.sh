#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$ROOT/../.." && pwd)
VERSION="0.1.0"
RUNTIME_VERSION="0.1.0"
ARCH="all"
PKG="goreecloud-care"
OUT=${1:-"$ROOT/dist"}

for command_name in git python3 dpkg-deb find touch install mktemp grep chmod; do
  command -v "$command_name" >/dev/null || {
    echo "Required command not found: $command_name" >&2
    exit 2
  }
done

# Release/acceptance provenance is bound to one exact committed source revision.
# The package intentionally refuses tracked dirty source so the embedded identity
# cannot describe different bytes than the files actually staged into the .deb.
if ! git -C "$REPO_ROOT" rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  echo "GoreeCloud Care package builds require the authoritative Git checkout." >&2
  exit 2
fi
if ! git -C "$REPO_ROOT" diff --quiet -- apps/goreecloud-care || \
   ! git -C "$REPO_ROOT" diff --cached --quiet -- apps/goreecloud-care; then
  echo "Tracked GoreeCloud Care source changes are present; commit/stash them before packaging." >&2
  exit 2
fi

require_tracked() {
  source_path=$1
  relative=${source_path#"$REPO_ROOT"/}
  git -C "$REPO_ROOT" ls-files --error-unmatch -- "$relative" >/dev/null 2>&1 || {
    echo "Package input is not part of the exact committed Care source: $relative" >&2
    exit 2
  }
}

# Every working-tree file that can enter the package must itself be tracked.
for packaged_source in \
  "$ROOT/packaging/postinst" \
  "$ROOT/packaging/postrm" \
  "$ROOT/packaging/goreecloud-care" \
  "$ROOT/packaging/goreecloud-care-helper" \
  "$ROOT/goreecloud_care/"*.py \
  "$ROOT/packaging/com.goreecloud.care.desktop" \
  "$ROOT/packaging/icons/com.goreecloud.care.svg" \
  "$ROOT/packaging/com.goreecloud.care.metainfo.xml" \
  "$ROOT/packaging/com.goreecloud.care.policy" \
  "$ROOT/LICENSE" \
  "$ROOT/API.md" \
  "$ROOT/WARDVEIL-INTEGRATION.md"; do
  require_tracked "$packaged_source"
done

SOURCE_REVISION=$(git -C "$REPO_ROOT" rev-parse HEAD)
SOURCE_TREE=$(git -C "$REPO_ROOT" rev-parse HEAD:apps/goreecloud-care)
printf '%s\n' "$SOURCE_REVISION" | grep -Eq '^[0-9a-f]{40}$' || {
  echo "Unable to resolve exact GoreeCloud Care source revision." >&2
  exit 2
}
printf '%s\n' "$SOURCE_TREE" | grep -Eq '^[0-9a-f]{40}$' || {
  echo "Unable to resolve exact GoreeCloud Care source tree." >&2
  exit 2
}

# Debian package output must be reproducible for an exact source revision. Use an
# explicit SOURCE_DATE_EPOCH when supplied; otherwise bind the package timestamp
# to the exact repository HEAD being built.
if [ -z "${SOURCE_DATE_EPOCH:-}" ]; then
  SOURCE_DATE_EPOCH=$(git -C "$REPO_ROOT" show -s --format=%ct HEAD)
fi
case "$SOURCE_DATE_EPOCH" in
  ''|*[!0-9]*)
    echo "SOURCE_DATE_EPOCH must be a non-negative integer Unix timestamp." >&2
    exit 2
    ;;
esac
export SOURCE_DATE_EPOCH

# Keep locale/timezone behavior deterministic and avoid compressor-version drift
# across the supported Zorin/Ubuntu build boundary. The package is small, so
# deterministic portability is more important than archive compression here.
export LC_ALL=C
export TZ=UTC

STAGE=$(mktemp -d)
chmod 0755 "$STAGE"
trap 'rm -rf "$STAGE"' EXIT INT TERM
mkdir -p "$OUT" \
  "$STAGE/DEBIAN" \
  "$STAGE/usr/bin" \
  "$STAGE/usr/lib/goreecloud-care/goreecloud_care" \
  "$STAGE/usr/share/applications" \
  "$STAGE/usr/share/icons/hicolor/scalable/apps" \
  "$STAGE/usr/share/metainfo" \
  "$STAGE/usr/share/polkit-1/actions" \
  "$STAGE/usr/share/doc/goreecloud-care" \
  "$STAGE/usr/share/goreecloud-care"
cat > "$STAGE/DEBIAN/control" <<CONTROL
Package: $PKG
Version: $VERSION
Section: utils
Priority: optional
Architecture: $ARCH
Maintainer: GoreeCloud <support@goreecloud.com>
Depends: python3, python3-gi, gir1.2-gtk-3.0, gir1.2-atk-1.0, policykit-1
Homepage: https://goreecloud.com/
Description: GoreeCloud Care local-first maintenance utility
 Local-first GTK maintenance utility for Zorin OS and compatible Linux systems.
CONTROL
chmod 0644 "$STAGE/DEBIAN/control"
install -m 0755 "$ROOT/packaging/postinst" "$STAGE/DEBIAN/postinst"
install -m 0755 "$ROOT/packaging/postrm" "$STAGE/DEBIAN/postrm"
install -m 0755 "$ROOT/packaging/goreecloud-care" "$STAGE/usr/bin/goreecloud-care"
install -m 0755 "$ROOT/packaging/goreecloud-care-helper" "$STAGE/usr/lib/goreecloud-care/goreecloud-care-helper"
install -m 0644 "$ROOT/goreecloud_care/"*.py "$STAGE/usr/lib/goreecloud-care/goreecloud_care/"
install -m 0644 "$ROOT/packaging/com.goreecloud.care.desktop" "$STAGE/usr/share/applications/com.goreecloud.care.desktop"
install -m 0644 "$ROOT/packaging/icons/com.goreecloud.care.svg" "$STAGE/usr/share/icons/hicolor/scalable/apps/com.goreecloud.care.svg"
install -m 0644 "$ROOT/packaging/com.goreecloud.care.metainfo.xml" "$STAGE/usr/share/metainfo/com.goreecloud.care.metainfo.xml"
install -m 0644 "$ROOT/packaging/com.goreecloud.care.policy" "$STAGE/usr/share/polkit-1/actions/"
install -m 0644 "$ROOT/LICENSE" "$STAGE/usr/share/doc/goreecloud-care/copyright"
install -m 0644 "$ROOT/API.md" "$STAGE/usr/share/doc/goreecloud-care/API.md"
install -m 0644 "$ROOT/WARDVEIL-INTEGRATION.md" "$STAGE/usr/share/doc/goreecloud-care/WARDVEIL-INTEGRATION.md"
cat > "$STAGE/usr/lib/goreecloud-care/goreecloud_care.pth" <<'PTH'
/usr/lib/goreecloud-care
PTH
chmod 0644 "$STAGE/usr/lib/goreecloud-care/goreecloud_care.pth"
mkdir -p "$STAGE/usr/lib/python3/dist-packages"
install -m 0644 "$STAGE/usr/lib/goreecloud-care/goreecloud_care.pth" "$STAGE/usr/lib/python3/dist-packages/goreecloud_care.pth"

# Package-owned build provenance lets installed Care bind later target/runtime
# acceptance to the exact Git source without relying on the invoking directory,
# user-writable state, or a retained .deb archive. The package SHA-256 remains an
# external acceptance property because embedding a package's own hash is circular.
python3 - "$STAGE/usr/share/goreecloud-care/build-provenance.json" \
  "$SOURCE_REVISION" "$SOURCE_TREE" "$RUNTIME_VERSION" "$VERSION" "$SOURCE_DATE_EPOCH" <<'PY'
import json
import sys
from pathlib import Path

out, revision, tree, runtime_version, package_version, epoch = sys.argv[1:]
payload = {
    "schema_version": 1,
    "application": "GoreeCloud Care",
    "producer": "GoreeCloud/goreecloud-zorin-os/apps/goreecloud-care",
    "source_revision": revision,
    "source_tree": tree,
    "runtime_version": runtime_version,
    "package_version": package_version,
    "source_date_epoch": int(epoch),
    "package_sha256_embedded": False,
}
Path(out).write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
PY
chmod 0644 "$STAGE/usr/share/goreecloud-care/build-provenance.json"

# Caller umask is not part of package identity or the installed trust boundary.
# mkdir and generated files otherwise inherit it, which can change package bytes
# and can make the provenance parent directory group-writable on a developer host.
find "$STAGE" -type d -exec chmod 0755 {} +

# Normalize every staged filesystem timestamp before dpkg-deb sees it. Explicit
# format 2.0 plus -Znone removes xz/zstd/gzip implementation differences from
# the byte-for-byte package identity.
find "$STAGE" -exec touch -h -d "@$SOURCE_DATE_EPOCH" {} +

dpkg-deb --root-owner-group --deb-format=2.0 -Znone --build "$STAGE" "$OUT/${PKG}_${VERSION}_${ARCH}.deb" >/dev/null
printf '%s\n' "$OUT/${PKG}_${VERSION}_${ARCH}.deb"
