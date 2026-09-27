#!/bin/sh
set -eu

ROOT=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
REPO_ROOT=$(CDPATH= cd -- "$ROOT/../.." && pwd)
PACKAGE_NAME="goreecloud-care_0.1.0_all.deb"
REFERENCE=${1:-"$ROOT/dist/$PACKAGE_NAME"}

for command_name in git cmp sha256sum awk mktemp mkdir rm sh; do
  command -v "$command_name" >/dev/null || {
    echo "Required command not found: $command_name" >&2
    exit 2
  }
done

[ -f "$REFERENCE" ] || {
  echo "Reference package not found: $REFERENCE" >&2
  exit 2
}

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

TMP=$(mktemp -d)
cleanup() {
  rm -rf "$TMP"
}
trap cleanup EXIT INT TERM
REBUILD_022_OUT="$TMP/rebuild-022"
REBUILD_002_OUT="$TMP/rebuild-002"
mkdir -p "$REBUILD_022_OUT" "$REBUILD_002_OUT"

# Rebuild under two common umasks. Package identity must not depend on whether a
# developer environment defaults newly created directories/files to 0755/0644
# or 0775/0664 before the build script applies canonical staged modes.
(
  umask 0022
  SOURCE_DATE_EPOCH="$SOURCE_DATE_EPOCH" sh "$ROOT/scripts/build-deb.sh" "$REBUILD_022_OUT" >/dev/null
)
(
  umask 0002
  SOURCE_DATE_EPOCH="$SOURCE_DATE_EPOCH" sh "$ROOT/scripts/build-deb.sh" "$REBUILD_002_OUT" >/dev/null
)
REBUILT_022="$REBUILD_022_OUT/$PACKAGE_NAME"
REBUILT_002="$REBUILD_002_OUT/$PACKAGE_NAME"
for rebuilt in "$REBUILT_022" "$REBUILT_002"; do
  [ -f "$rebuilt" ] || {
    echo "Rebuilt package not found: $rebuilt" >&2
    exit 1
  }
done

REFERENCE_SHA=$(sha256sum "$REFERENCE" | awk '{print $1}')
REBUILT_022_SHA=$(sha256sum "$REBUILT_022" | awk '{print $1}')
REBUILT_002_SHA=$(sha256sum "$REBUILT_002" | awk '{print $1}')

if ! cmp -s "$REBUILT_022" "$REBUILT_002"; then
  echo "Reproducible package verification failed across umasks." >&2
  echo "umask 0022 SHA-256: $REBUILT_022_SHA" >&2
  echo "umask 0002 SHA-256: $REBUILT_002_SHA" >&2
  echo "SOURCE_DATE_EPOCH: $SOURCE_DATE_EPOCH" >&2
  exit 1
fi

for rebuilt in "$REBUILT_022" "$REBUILT_002"; do
  if ! cmp -s "$REFERENCE" "$rebuilt"; then
    echo "Reproducible package verification failed." >&2
    echo "Reference SHA-256:  $REFERENCE_SHA" >&2
    echo "umask 0022 SHA-256: $REBUILT_022_SHA" >&2
    echo "umask 0002 SHA-256: $REBUILT_002_SHA" >&2
    echo "SOURCE_DATE_EPOCH: $SOURCE_DATE_EPOCH" >&2
    exit 1
  fi
done

printf '%s\n' "Reproducible package verification: passed"
printf '%s\n' "Umask independence: passed (0022 == 0002)"
printf '%s\n' "SOURCE_DATE_EPOCH: $SOURCE_DATE_EPOCH"
printf '%s\n' "SHA-256: $REFERENCE_SHA"
